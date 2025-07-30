import functools
import logging
import tempfile
import time
from pathlib import Path
from typing import Any, Optional, Union

import mlflow
import mlflow.pytorch
import torch

from .onnx_client import OnnxClient

# onnx_client 인스턴스 생성
onnx_client = OnnxClient()
logger = logging.getLogger(__name__)


# ============================================================================
# 유틸리티 함수들
# ============================================================================


def _convert_to_numpy(
    tensor_data: Union[torch.Tensor, dict[str, torch.Tensor], tuple, list],
) -> Union[Any, dict[str, Any]]:
    """PyTorch 텐서를 NumPy 배열로 변환 (MLflow infer_signature 용)."""
    if isinstance(tensor_data, torch.Tensor):
        return tensor_data.detach().cpu().numpy()
    elif isinstance(tensor_data, dict):
        return {key: _convert_to_numpy(value) for key, value in tensor_data.items()}
    elif isinstance(tensor_data, (tuple, list)):
        return [_convert_to_numpy(item) for item in tensor_data]
    else:
        return tensor_data


def _infer_model_schema(
    model: torch.nn.Module, sample_input: Union[torch.Tensor, dict[str, torch.Tensor]]
) -> "mlflow.models.signature.ModelSignature":
    """
    PyTorch 모델로부터 자동으로 입력/출력 스키마 추출

    Args:
        model: PyTorch 모델
        sample_input: 샘플 입력 (실제 모델 실행용)

    Returns:
        ModelSignature: 자동 추출된 스키마

    """
    from mlflow.models.signature import infer_signature

    model.eval()
    device = next(model.parameters()).device

    # 샘플 입력을 모델과 같은 디바이스로 이동
    if isinstance(sample_input, torch.Tensor):
        sample_input = sample_input.to(device)
    elif isinstance(sample_input, dict):
        sample_input = {k: v.to(device) for k, v in sample_input.items()}

    # 실제 모델 실행하여 출력 확인
    with torch.no_grad():
        if isinstance(sample_input, dict):
            sample_output = model(**sample_input)
        else:
            sample_output = model(sample_input)

    # PyTorch 텐서를 NumPy로 변환
    numpy_input = _convert_to_numpy(sample_input)
    numpy_output = _convert_to_numpy(sample_output)

    # MLflow 자동 추론 사용
    signature = infer_signature(numpy_input, numpy_output)

    logger.info(f"자동 추출된 스키마: {signature}")
    return signature


def _generate_input_output_names(
    signature: "mlflow.models.signature.ModelSignature",
) -> tuple[list[str], list[str]]:
    """
    MLflow signature로부터 input/output 이름들을 생성합니다.

    다양한 MLflow 버전 호환성을 고려합니다.
    """
    input_names: list[str] = []
    output_names: list[str] = []

    # 입력 이름 생성 - 여러 방법 시도
    try:
        # 방법 2: 스키마에서 이름 추출
        if not input_names and hasattr(signature.inputs, "schema"):
            schema = signature.inputs.schema
            if hasattr(schema, "names") and schema.names:
                input_names = list(schema.names)
            elif hasattr(schema, "input_names") and callable(schema.input_names):
                potential_names = schema.input_names()
                if potential_names:
                    input_names = list(potential_names)

        # 방법 3: 텐서 정보에서 추출 시도
        if not input_names:
            try:
                input_spec = str(signature.inputs)
                if "'" in input_spec:  # 'image': Tensor, 'mask': Tensor 형태
                    import re

                    names = re.findall(r"'([^']+)':", input_spec)
                    if names:
                        input_names = names
            except Exception:
                pass

        # 방법 4: 기본 이름 생성
        if not input_names:
            # signature.inputs를 분석하여 개수 추정
            inputs_str = str(signature.inputs)
            if "Tensor" in inputs_str:
                tensor_count = inputs_str.count("Tensor")
                input_names = [f"input_{i}" for i in range(max(1, tensor_count))]
            else:
                input_names = ["input_0"]

    except Exception as e:
        logger.debug(f"입력 이름 생성 중 오류: {e}")
        input_names = ["input_0"]

    # 출력 이름 생성 - 유사한 방법들
    try:
        # MLflow outputs는 일반적으로 input_names 메서드가 없음
        if hasattr(signature.outputs, "schema"):
            schema = signature.outputs.schema
            if hasattr(schema, "names") and schema.names:
                output_names = list(schema.names)

        # 기본 이름 생성
        if not output_names:
            outputs_str = str(signature.outputs)
            if "Tensor" in outputs_str:
                tensor_count = outputs_str.count("Tensor")
                output_names = [f"output_{i}" for i in range(max(1, tensor_count))]
            else:
                output_names = ["output_0"]

    except Exception as e:
        logger.debug(f"출력 이름 생성 중 오류: {e}")
        output_names = ["output_0"]

    logger.debug(f"생성된 이름 - 입력: {input_names}, 출력: {output_names}")
    return input_names, output_names


def _convert_pytorch_to_onnx_with_client(
    model: torch.nn.Module,
    sample_input: Union[torch.Tensor, dict[str, torch.Tensor]],
    signature: "mlflow.models.signature.ModelSignature",
    onnx_opset_version: int = 17,
    custom_dynamic_axes: Optional[dict[str, dict[int, str]]] = None,  # 새로 추가
) -> Optional[str]:
    """
    PyTorch 모델을 ONNX로 변환하고 onnx_client를 통해 업로드합니다.

    Args:
        model: PyTorch 모델
        sample_input: 샘플 입력
        signature: MLflow 시그니처
        onnx_opset_version: ONNX opset 버전
        custom_dynamic_axes: 사용자 정의 dynamic_axes (선택사항)

    Returns:
        Optional[str]: 업로드된 모델 경로 (프로덕션 모드가 아닌 경우)

    """
    try:
        # 스키마로부터 input/output 이름 자동 생성
        input_names, output_names = _generate_input_output_names(signature)

        logger.info(f"ONNX 변환 시작 - 입력: {input_names}, 출력: {output_names}")

        # 임시 ONNX 파일 생성
        with tempfile.NamedTemporaryFile(suffix=".onnx", delete=False) as tmp_file:
            onnx_path = tmp_file.name

        conversion_start = time.time()

        # 🎯 개선된 dynamic_axes 구성
        dynamic_axes = {}

        # 1. 기본 배치 차원 설정 (모든 입력/출력에 적용)
        for input_name in input_names:
            dynamic_axes[input_name] = {0: "batch_size"}

        for output_name in output_names:
            dynamic_axes[output_name] = {0: "batch_size"}

        # 2. 사용자 정의 dynamic_axes 병합
        if custom_dynamic_axes:
            for tensor_name, axes_dict in custom_dynamic_axes.items():
                if tensor_name in dynamic_axes:
                    # 기존 축 정보와 병합
                    dynamic_axes[tensor_name].update(axes_dict)
                else:
                    # 새로운 텐서 추가
                    dynamic_axes[tensor_name] = axes_dict.copy()

        logger.info(f"최종 Dynamic axes 구성: {dynamic_axes}")

        # PyTorch → ONNX 변환 (호환성 우선)
        # sample_input을 적절한 형태로 변환
        export_args: Any
        if isinstance(sample_input, torch.Tensor):
            export_args = (sample_input,)
        elif isinstance(sample_input, dict):
            # dict 형태의 입력은 그대로 사용
            export_args = sample_input
        else:
            export_args = sample_input

        try:
            # 동적 크기 지원 시도
            torch.onnx.export(
                model,
                export_args,  # type: ignore[arg-type]
                onnx_path,
                export_params=True,
                opset_version=onnx_opset_version,
                do_constant_folding=True,
                input_names=input_names,
                output_names=output_names,
                dynamic_axes=dynamic_axes,
                verbose=False,
            )
            logger.info("동적 크기 ONNX 모델 변환 완료")

        except Exception as e:
            # 고정 크기로 재시도 (dynamic_axes 제거)
            logger.warning(
                f"동적 크기 ONNX 변환 실패, 고정 크기로 재시도: {str(e)[:100]}..."
            )
            try:
                torch.onnx.export(
                    model,
                    export_args,  # type: ignore[arg-type]
                    onnx_path,
                    export_params=True,
                    opset_version=onnx_opset_version,
                    do_constant_folding=True,
                    input_names=input_names,
                    output_names=output_names,
                    verbose=False,
                )
                logger.info("고정 크기 ONNX 모델 변환 완료")
            except Exception as e2:
                # 최소한의 설정으로 마지막 시도
                logger.warning(
                    f"표준 ONNX 변환도 실패, 최소 설정으로 재시도: {str(e2)[:100]}..."
                )
                torch.onnx.export(
                    model,
                    export_args,  # type: ignore[arg-type]
                    onnx_path,
                    export_params=True,
                    opset_version=onnx_opset_version,
                )
                logger.info("최소 설정 ONNX 모델 변환 완료")

        conversion_time = time.time() - conversion_start

        onnx_path_obj = Path(onnx_path)
        if not onnx_path_obj.exists():
            raise FileNotFoundError("ONNX 파일이 생성되지 않았습니다.")

        file_size_mb = onnx_path_obj.stat().st_size / (1024 * 1024)

        # ONNX 메타데이터 로깅
        onnx_metadata = {
            "onnx_conversion_time": conversion_time,
            "onnx_file_size_mb": file_size_mb,
            "onnx_opset_version": onnx_opset_version,
        }
        mlflow.log_metrics(onnx_metadata)
        mlflow.log_params(
            {
                "onnx_input_names": input_names,
                "onnx_output_names": output_names,
            }
        )

        logger.info(f"ONNX 변환 완료: {onnx_path} ({file_size_mb:.2f}MB)")

        # 🔥 onnx_client를 통한 업로드 및 RabbitMQ 발행
        try:
            upload_result = onnx_client.upload(onnx_path)
            logger.info("✅ ONNX 모델 업로드 및 RabbitMQ 발행 완료")

            # 임시 파일 정리
            onnx_path_obj.unlink()

            return upload_result

        except Exception as e:
            logger.error(f"ONNX 클라이언트 업로드 실패: {e}")
            # 임시 파일 정리
            if onnx_path_obj.exists():
                onnx_path_obj.unlink()
            raise

    except Exception as e:
        logger.error(f"ONNX 변환 실패: {e}")
        mlflow.log_param("onnx_conversion_error", str(e))
        return None


# ============================================================================
# 새로운 완전 자동화된 API (MLflow 3.11.1 auto-inference 활용)
# ============================================================================


def trace_pytorch(
    experiment_name: str,
    sample_input: Union[torch.Tensor, dict[str, torch.Tensor]],
    run_name: Optional[str] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
    onnx_opset_version: int = 17,
    auto_convert_onnx: bool = True,
    log_model_info: bool = True,
    enable_autolog: bool = True,
    dynamic_axes: Optional[dict[str, dict[int, str]]] = None,
):
    """
    완전 자동화된 PyTorch 모델 추적 (MLflow 3.11.1 auto-inference 활용)

    사용자는 decorator에 샘플 입력을 제공하고, 함수에서는 모델만 반환하면 됩니다.
    실제 모델 실행으로 정확한 스키마를 자동 추출합니다.

    Args:
        experiment_name: MLflow 실험 이름
        sample_input: 샘플 입력 (torch.Tensor 또는 Dict[str, torch.Tensor])
        run_name: MLflow 런 이름 (선택사항)
        device: 디바이스 ("cuda" 또는 "cpu")
        onnx_opset_version: ONNX opset 버전
        auto_convert_onnx: PyTorch → ONNX 자동 변환 여부
        log_model_info: 모델 정보 로깅 여부
        enable_autolog: MLflow autolog 활성화 여부

    Returns:
        함수 decorator

    사용 예시:
        ```python
        # 기본 사용법 (ONNX 변환 + MLflow 로깅)
        @trace_pytorch("my_experiment", torch.randn(1, 3, 224, 224))
        def train_model():
            model = MyModel()

            # 학습 중 메트릭 로깅 (권장)
            for epoch in range(epochs):
                # 학습 코드...
                train_loss, train_acc = train_one_epoch(model, ...)
                mlflow.log_metrics({
                    "train_loss": train_loss,
                    "train_accuracy": train_acc
                }, step=epoch)

            return model  # 모델만 반환!

        # 다중 입력 모델
        @trace_pytorch("multi_experiment", {
            "image": torch.randn(1, 3, 224, 224),
            "mask": torch.randn(1, 1, 224, 224)
        })
        def train_multi_input_model():
            model = MultiInputModel()
            # 학습 코드...
            return model

        # ONNX 변환 비활성화 (MLflow만 사용)
        @trace_pytorch"mlflow_only", torch.randn(1, 3, 224, 224), auto_convert_onnx=False)
        def train_model_no_onnx():
            model = MyModel()
            # 학습 코드...
            return model
        ```

    """
    # 디바이스 검증
    if not torch.cuda.is_available() and device == "cuda":
        logger.warning("CUDA가 사용 불가하므로 CPU로 변경합니다.")
        device = "cpu"

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if enable_autolog:
                mlflow.pytorch.autolog()
                logger.info("✅ MLflow PyTorch autolog 활성화 완료")
            else:
                mlflow.pytorch.autolog(disable=True)
                logger.info("🚫 MLflow PyTorch autolog 비활성화")

            # 실험 설정
            experiment = mlflow.get_experiment_by_name(experiment_name)
            if experiment is None:
                experiment_id = mlflow.create_experiment(experiment_name)
                logger.info(f"새 실험 생성: {experiment_name}")
            else:
                experiment_id = experiment.experiment_id
                logger.info(f"기존 실험 사용: {experiment_name}")

            start_time = time.time()

            with mlflow.start_run(
                experiment_id=experiment_id, run_name=run_name
            ) as run:
                try:
                    logger.info(f"MLflow 실행 시작 (run_id: {run.info.run_id})")

                    # 사용자 함수 실행
                    result = func(*args, **kwargs)

                    # 반환값 검증 - 모델만 반환해야 함!
                    if not isinstance(result, torch.nn.Module):
                        raise ValueError(
                            "함수는 torch.nn.Module만 반환해야 합니다.\n"
                            f"받은 타입: {type(result)}\n"
                            "예시: return model"
                        )

                    model = result

                    # 모델을 지정된 디바이스로 이동
                    model = model.to(device)
                    logger.info(f"모델이 {device} 디바이스로 이동되었습니다.")

                    # sample_input도 동일한 디바이스로 이동
                    if isinstance(sample_input, torch.Tensor):
                        device_sample_input = sample_input.to(device)
                    elif isinstance(sample_input, dict):
                        device_sample_input = {
                            k: v.to(device) for k, v in sample_input.items()
                        }
                    else:
                        raise ValueError(
                            f"지원되지 않는 sample_input 타입: {type(sample_input)}"
                        )

                    # 🚀 핵심: 실제 모델로부터 스키마 자동 추출
                    signature = _infer_model_schema(model, device_sample_input)

                    # 모델 정보 로깅
                    if log_model_info:
                        model_info = {
                            "model_class": model.__class__.__name__,
                            "device": str(device),
                            "total_params": sum(p.numel() for p in model.parameters()),
                            "trainable_params": sum(
                                p.numel() for p in model.parameters() if p.requires_grad
                            ),
                        }

                        # 입력 정보 자동 추출
                        if isinstance(device_sample_input, torch.Tensor):
                            model_info["input_shape"] = tuple(device_sample_input.shape)
                            model_info["input_dtype"] = str(device_sample_input.dtype)
                        elif isinstance(device_sample_input, dict):
                            model_info["input_shapes"] = {
                                k: tuple(v.shape)
                                for k, v in device_sample_input.items()
                            }
                            model_info["input_dtypes"] = {
                                k: str(v.dtype) for k, v in device_sample_input.items()
                            }

                        mlflow.log_params(model_info)
                        logger.info(f"모델 정보 로깅 완료: {model_info['model_class']}")

                    # 🤝 Autolog와 수동 로깅의 조화
                    # autolog가 활성화되어 있으면 중복 로깅 방지
                    if not enable_autolog:
                        # autolog가 비활성화된 경우에만 수동으로 모델 로깅
                        model_info = mlflow.pytorch.log_model(
                            pytorch_model=model,
                            artifact_path="model",
                            signature=signature,
                            input_example=_convert_to_numpy(device_sample_input),
                        )
                        logger.info("PyTorch 모델 수동 로깅 완료")
                    else:
                        logger.info("PyTorch 모델은 autolog에 의해 자동 로깅됩니다")

                    # 🔥 ONNX 변환 및 업로드 (onnx_client 활용)
                    if auto_convert_onnx:
                        upload_result = _convert_pytorch_to_onnx_with_client(
                            model=model,
                            sample_input=device_sample_input,
                            signature=signature,
                            onnx_opset_version=onnx_opset_version,
                            custom_dynamic_axes=dynamic_axes,  # 새로 추가
                        )

                        if upload_result:
                            mlflow.log_param("onnx_upload_path", upload_result)
                            mlflow.log_param(
                                "custom_dynamic_axes", str(dynamic_axes)
                            )  # 로깅 추가
                            logger.info(
                                f"🚀 ONNX 모델 서비스 업로드 완료: {upload_result}"
                            )
                        else:
                            logger.warning("⚠️ ONNX 업로드 실패")

                    # 실행 시간 로깅
                    total_time = time.time() - start_time
                    mlflow.log_metric("total_execution_time", total_time)

                    logger.info(f"🎉 모델 추적 완료 (실행시간: {total_time:.2f}초)")
                    logger.info(f"자동 추출된 스키마: {signature}")

                    return model

                except Exception as e:
                    logger.error(f"모델 추적 실패: {e}")
                    mlflow.log_param("execution_error", str(e))
                    raise

        return wrapper

    return decorator


# ============================================================================
# 프레임워크 독립적인 ONNX 모델 로깅 API
# ============================================================================


def log_onnx_model(
    experiment_name: str,
    onnx_model_path: Union[str, Path],
    run_name: Optional[str] = None,
    model_name: Optional[str] = None,
    signature: Optional["mlflow.models.signature.ModelSignature"] = None,
    input_example: Optional[Union[Any, dict[str, Any]]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """
    프레임워크 독립적인 ONNX 모델 로깅 및 배포

    PyTorch가 아닌 다른 프레임워크(TensorFlow, JAX, MXNet 등)에서
    학습한 모델을 ONNX로 변환한 후, 이 함수를 사용하여 MLflow에
    로깅하고 추론 서비스에 배포할 수 있습니다.

    이 함수는 @trace_pytorch 데코레이터를 사용할 수 없는 상황에서
    ONNX 모델을 직접 업로드하기 위한 대안입니다.

    Args:
        experiment_name: MLflow 실험 이름
        onnx_model_path: ONNX 모델 파일 경로
        run_name: MLflow 런 이름 (선택사항)
        model_name: 모델 이름 (선택사항, 기본값: 파일명)
        signature: MLflow 모델 시그니처 (선택사항)
        input_example: 입력 예시 (선택사항)
        metadata: 추가 메타데이터 (선택사항)

    Returns:
        Optional[str]: 업로드된 모델 경로 (프로덕션 모드가 아닌 경우)

    사용 예시:
        ```python
        # TensorFlow 모델 사용 예
        import tensorflow as tf
        import tf2onnx

        # TensorFlow 모델을 ONNX로 변환
        model = tf.keras.models.load_model('my_model.h5')
        spec = (tf.TensorSpec((None, 224, 224, 3), tf.float32, name="input"),)
        output_path = "model.onnx"

        model_proto, _ = tf2onnx.convert.from_keras(model, input_signature=spec)
        with open(output_path, "wb") as f:
            f.write(model_proto.SerializeToString())

        # ONNX 모델 로깅 및 업로드
        upload_path = log_onnx_model(
            experiment_name="tensorflow_experiment",
            onnx_model_path=output_path,
            metadata={"framework": "tensorflow", "model_type": "classification"}
        )

        # JAX/Flax 모델 사용 예
        # ... JAX 모델을 ONNX로 변환 ...
        upload_path = log_onnx_model(
            experiment_name="jax_experiment",
            onnx_model_path="jax_model.onnx",
            metadata={"framework": "jax", "optimizer": "adam"}
        )
        ```

    """
    try:
        # 경로 객체로 변환
        onnx_path = Path(onnx_model_path)
        if not onnx_path.exists():
            raise FileNotFoundError(f"ONNX 모델 파일을 찾을 수 없습니다: {onnx_path}")

        # ONNX 파일 검증
        if onnx_path.suffix.lower() != ".onnx":
            logger.warning(f"파일 확장자가 .onnx가 아닙니다: {onnx_path.suffix}")

        # 파일 크기 검증 (최소 크기)
        file_size = onnx_path.stat().st_size
        if file_size < 1024:  # 1KB 미만
            logger.warning(f"ONNX 파일 크기가 매우 작습니다: {file_size} bytes")

        # 모델 이름 설정
        if model_name is None:
            model_name = onnx_path.stem

        # 실험 설정
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            experiment_id = mlflow.create_experiment(experiment_name)
            logger.info(f"새 실험 생성: {experiment_name}")
        else:
            experiment_id = experiment.experiment_id
            logger.info(f"기존 실험 사용: {experiment_name}")

        start_time = time.time()

        with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run:
            logger.info(f"MLflow 실행 시작 (run_id: {run.info.run_id})")

            # 메타데이터 로깅
            if metadata:
                mlflow.log_params(metadata)

            # 기본 정보 로깅
            file_size_mb = onnx_path.stat().st_size / (1024 * 1024)
            mlflow.log_params(
                {
                    "model_name": model_name,
                    "onnx_file_size_mb": file_size_mb,
                    "source_framework": (
                        metadata.get("framework", "unknown") if metadata else "unknown"
                    ),
                }
            )

            # ONNX 모델을 MLflow에 로깅
            import onnx
            onnx_model = onnx.load(str(onnx_path))
            mlflow.onnx.log_model(
                onnx_model=onnx_model,
                artifact_path="model",
                signature=signature,
                input_example=input_example,
            )
            logger.info("ONNX 모델 MLflow 로깅 완료")

            # onnx_client를 통한 업로드
            try:
                upload_result = onnx_client.upload(onnx_path)
                if upload_result:
                    mlflow.log_param("onnx_upload_path", upload_result)
                    logger.info(f"🚀 ONNX 모델 서비스 업로드 완료: {upload_result}")
                else:
                    logger.warning("⚠️ ONNX 업로드 실패")

            except Exception as e:
                logger.error(f"ONNX 클라이언트 업로드 실패: {e}")
                mlflow.log_param("upload_error", str(e))
                upload_result = None

            # 실행 시간 로깅
            total_time = time.time() - start_time
            mlflow.log_metric("total_execution_time", total_time)

            logger.info(f"🎉 ONNX 모델 로깅 완료 (실행시간: {total_time:.2f}초)")

            return upload_result

    except Exception as e:
        logger.error(f"ONNX 모델 로깅 실패: {e}")
        raise
