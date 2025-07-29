import json
import logging
from pathlib import Path
from typing import Optional, Union

import mlflow
import numpy as np
import onnx
import onnxruntime as ort
from mlflow.models import infer_signature

from .base_mlflow_client import BaseMLflowClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OnnxClient(BaseMLflowClient):
    def __init__(self):
        super().__init__()

    def upload(
        self,
        model: Union[onnx.ModelProto, str, bytes, Path],
    ) -> Optional[str]:
        """
        ONNX 모델을 MLflow에 업로드하고 필요한 경우 RabbitMQ에 알림을 보냅니다.

        Args:
            model: ONNX 모델 또는 모델 경로

        Returns:
            Optional[str]: 프로덕션 모드가 아닌 경우 모델 경로 반환

        Raises:
            Exception: 모델 업로드 중 오류 발생

        """
        try:
            logger.info("ONNX 모델 유효성 검사 시작")

            # 파일 경로인 경우 모델 로드
            if isinstance(model, (str, Path)):
                logger.debug(f"모델 파일 로드 중: {model}")
                model_proto = onnx.load(str(model))
            elif isinstance(model, onnx.ModelProto):
                model_proto = model
            else:
                raise ValueError(
                    "model must be either a file path or an ONNX ModelProto"
                )

            # ONNX 모델 유효성 검사
            onnx.checker.check_model(model_proto)
            logger.info("✅ ONNX 모델 유효성 검사 완료")

            # 텐서 정보 로깅
            self._log_tensor(model_proto)

            # MLflow 3.11.1: input_example을 사용하여 자동 signature 추론
            input_example = self._get_input_example(model_proto)

            # MLflow에 모델 로깅
            path = self._log_model(model=model_proto, input_example=input_example)

            # 프로덕션 모드가 아닌 경우 RabbitMQ 건너뜀
            if not self.is_production:
                logger.info("개발 모드: RabbitMQ 메시지 전송 건너뜀")
                return path

            # RabbitMQ에 모델 업로드 알림 발행
            self._publish_to_rabbitmq(path)
            logger.info("🚀 ONNX 모델 업로드 및 RabbitMQ 발행 완료")

            return path

        except Exception as e:
            logger.error(f"ONNX 모델 업로드 중 오류 발생: {e!s}", exc_info=True)
            raise

    def _get_input_example(
        self, onnx_model: onnx.ModelProto
    ) -> Union[np.ndarray, dict[str, np.ndarray]]:
        """
        ONNX 모델의 입력 스키마를 분석하여 입력 예제를 생성합니다.

        다중 입력을 지원합니다.

        Args:
            onnx_model: ONNX 모델

        Returns:
            Union[np.ndarray, dict[str, np.ndarray]]: 단일 입력인 경우 배열, 다중 입력인 경우 딕셔너리

        Raises:
            ValueError: 입력 텐서가 없는 경우
            Exception: 입력 예제 생성 중 오류 발생

        """
        try:
            input_tensors = onnx_model.graph.input

            if not input_tensors:
                raise ValueError("ONNX 모델에 입력 텐서가 정의되지 않았습니다.")

            # 단일 입력인 경우
            if len(input_tensors) == 1:
                input_tensor = input_tensors[0]
                input_example = self._create_tensor_example(input_tensor)
                logger.debug(
                    f"단일 입력 예제 생성: 형태={input_example.shape}, 타입={input_example.dtype}"
                )
                return input_example

            # 다중 입력인 경우
            else:
                input_examples = {}
                for input_tensor in input_tensors:
                    input_name = input_tensor.name
                    input_example = self._create_tensor_example(input_tensor)
                    input_examples[input_name] = input_example
                    logger.debug(
                        f"다중 입력 예제 생성: {input_name}, 형태={input_example.shape}, 타입={input_example.dtype}"
                    )

                logger.info(f"다중 입력 예제 생성 완료: {len(input_examples)}개 입력")
                return input_examples

        except Exception as e:
            logger.error(f"입력 예제 생성 중 오류 발생: {e!s}", exc_info=True)
            raise

    def _create_tensor_example(self, input_tensor) -> np.ndarray:
        """
        개별 텐서에 대한 예제 데이터를 생성합니다.

        Args:
            input_tensor: ONNX 입력 텐서

        Returns:
            np.ndarray: 예제 데이터

        Raises:
            ValueError: 지원되지 않는 데이터 타입

        """
        # 데이터 타입 및 형태 추출
        dtype = self.get_triton_compatible_type(input_tensor.type.tensor_type)
        shape = [
            dim.dim_value if dim.dim_value > 0 else 1  # 동적 차원은 1로 설정
            for dim in input_tensor.type.tensor_type.shape.dim
        ]

        # 빈 shape 처리
        if not shape:
            shape = [1]

        # NumPy 데이터 타입 변환
        numpy_dtype = self._get_numpy_dtype(dtype)

        # 효율적인 예제 데이터 생성 (랜덤 대신 zeros 사용으로 메모리 효율성 향상)
        if numpy_dtype in [np.bool_, np.uint8, np.int32, np.int64]:
            # 정수형/불린형은 zeros
            input_example = np.zeros(shape, dtype=numpy_dtype)
        else:
            # 실수형은 작은 랜덤 값 (일부 모델에서 zero 입력 시 문제가 있을 수 있음)
            input_example = np.random.rand(*shape).astype(numpy_dtype) * 0.1

        return input_example

    def _process_tensors(self, tensors) -> dict[str, np.ndarray]:
        """
        텐서 정보를 처리하여 스키마 파라미터를 생성합니다.

        Args:
            tensors: 텐서 리스트

        Returns:
            dict[str, np.ndarray]: 텐서 이름을 키로 하는 딕셔너리

        """
        schema_params = {}
        for tensor in tensors:
            name = tensor.name
            dtype = self.get_triton_compatible_type(tensor.type.tensor_type)
            shape = [
                dim.dim_value if dim.dim_value > 0 else 1  # 동적 차원은 1로 설정
                for dim in tensor.type.tensor_type.shape.dim
            ]

            numpy_dtype = self._get_numpy_dtype(dtype)
            schema_params[name] = np.ones(shape, dtype=numpy_dtype)
            logger.debug(f"텐서 처리: {name}, 형태: {shape}, 타입: {dtype}")

        return schema_params

    def _publish_to_rabbitmq(self, path: str) -> None:
        """
        RabbitMQ에 모델 업로드 메시지를 발행합니다.

        Args:
            path: 업로드된 모델 경로

        Raises:
            Exception: RabbitMQ 메시지 발행 실패

        """
        channel = None
        try:
            channel = self.get_connection().channel()

            message = json.dumps(
                {"train_id": self.train_id, "full_path": path}, ensure_ascii=False
            )

            channel.basic_publish(
                exchange=self._uploadModelExchange,
                routing_key=self._uploadModelExchange,
                body=message,
            )
            logger.info(f"RabbitMQ에 모델 업로드 메시지 발행 완료: {message}")

        except Exception as e:
            logger.error(f"RabbitMQ 메시지 발행 실패: {e!s}", exc_info=True)
            raise
        finally:
            if channel:
                channel.close()

    def _log_model(
        self,
        model: onnx.ModelProto,
        input_example: Union[np.ndarray, dict[str, np.ndarray]],
    ) -> str:
        """
        MLflow에 ONNX 모델을 로깅합니다.

        Args:
            model: ONNX 모델
            input_example: 자동 signature 추론을 위한 입력 예제

        Returns:
            str: 로깅된 모델의 전체 경로

        Raises:
            Exception: 모델 로깅 중 오류 발생

        """
        try:
            # ONNX 모델의 출력 예제를 생성하여 signature 추론
            output_example = self._create_output_example(model, input_example)

            # 명시적으로 이름이 포함된 signature 생성
            signature = self._create_named_signature(
                model, input_example, output_example
            )

            # 모델 크기 확인 (2GB = 2 * 1024 * 1024 * 1024 bytes)
            model_size_bytes = len(model.SerializeToString())
            model_size_gb = model_size_bytes / (1024 * 1024 * 1024)

            # 큰 모델(2GB 이상)인 경우에만 외부 데이터로 저장
            save_externally = model_size_gb >= 2.0

            logger.debug(
                f"모델 크기: {model_size_gb:.3f}GB, 외부 저장: {save_externally}"
            )

            # MLflow 3.11.1: signature를 명시적으로 전달
            model_info = mlflow.onnx.log_model(
                onnx_model=model,
                artifact_path=self.model_name,
                input_example=input_example,
                signature=signature,  # 명시적으로 생성된 signature 전달
                # MLflow 3.11.1 추가 옵션들
                registered_model_name=None,  # 필요시 등록된 모델명 지정 가능
                await_registration_for=None,  # 등록 대기 시간
                metadata={
                    "framework": "onnx",
                    "source": "pytorch_trace",
                    "model_size_gb": f"{model_size_gb:.3f}",
                },  # 메타데이터 추가
                # ONNX 모델 특화 옵션: 2GB 이상일 때만 외부 저장
                save_as_external_data=save_externally,
            )

            # 실제 artifact URI 구성 (MLflow 3.x 호환)
            logger.info(f"MLflow에 ONNX 모델 저장 완료: {model_info.artifact_path}")

            return model_info.artifact_path

        except Exception as e:
            logger.error(f"ONNX 모델 로깅 중 오류 발생: {e!s}", exc_info=True)
            raise

    def _create_named_signature(
        self,
        model: onnx.ModelProto,
        input_example: Union[np.ndarray, dict[str, np.ndarray]],
        output_example: Union[np.ndarray, dict[str, np.ndarray]],
    ) -> "mlflow.models.signature.ModelSignature":
        """
        ONNX 모델에서 이름이 포함된 signature를 생성합니다.

        Args:
            model: ONNX 모델
            input_example: 입력 예제
            output_example: 출력 예제

        Returns:
            ModelSignature: 이름이 포함된 signature

        """
        from mlflow.models.signature import ModelSignature
        from mlflow.types import ColSpec, Schema, TensorSpec

        try:
            # ONNX Runtime을 사용하여 실제 입력 이름 가져오기 (초기화 텐서 제외)
            model_bytes = model.SerializeToString()
            session = ort.InferenceSession(
                model_bytes, providers=["CPUExecutionProvider"]
            )

            # 실제 입력 이름들 (초기화 텐서 제외)
            actual_input_names = [
                input_meta.name for input_meta in session.get_inputs()
            ]

            # ONNX Runtime을 사용하여 실제 출력 이름 가져오기
            actual_output_names = [
                output_meta.name for output_meta in session.get_outputs()
            ]

            logger.debug(
                f"ONNX 모델의 실제 텐서 이름 - 입력: {actual_input_names}, 출력: {actual_output_names}"
            )

            input_specs: list[ColSpec | TensorSpec] = []

            if isinstance(input_example, dict):
                # 다중 입력인 경우
                for input_name in actual_input_names:
                    if input_name in input_example:
                        example_data = input_example[input_name]
                        input_spec = TensorSpec(
                            type=example_data.dtype,
                            shape=[
                                -1,
                                *list(example_data.shape[1:]),
                            ],  # 배치 차원을 동적으로 설정
                            name=input_name,
                        )
                        input_specs.append(input_spec)
            else:
                # 단일 입력인 경우
                input_name = actual_input_names[0]
                input_spec = TensorSpec(
                    type=input_example.dtype,
                    shape=[
                        -1,
                        *list(input_example.shape[1:]),
                    ],  # 배치 차원을 동적으로 설정
                    name=input_name,
                )
                input_specs.append(input_spec)

            output_specs: list[ColSpec | TensorSpec] = []

            if isinstance(output_example, dict):
                # 다중 출력인 경우
                for output_name in actual_output_names:
                    if output_name in output_example:
                        example_data = output_example[output_name]
                        output_spec = TensorSpec(
                            type=example_data.dtype,
                            shape=[
                                -1,
                                *list(example_data.shape[1:]),
                            ],  # 배치 차원을 동적으로 설정
                            name=output_name,
                        )
                        output_specs.append(output_spec)
            else:
                # 단일 출력인 경우
                output_name = actual_output_names[0]
                output_spec = TensorSpec(
                    type=output_example.dtype,
                    shape=[
                        -1,
                        *list(output_example.shape[1:]),
                    ],  # 배치 차원을 동적으로 설정
                    name=output_name,
                )
                output_specs.append(output_spec)

            # Schema 생성
            input_schema = Schema(input_specs)
            output_schema = Schema(output_specs)

            # ModelSignature 생성
            signature = ModelSignature(inputs=input_schema, outputs=output_schema)

            logger.info(f"이름이 포함된 signature 생성 완료: {signature}")
            return signature

        except Exception as e:
            logger.error(f"Named signature 생성 중 오류 발생: {e!s}", exc_info=True)
            # 실패 시 기본 infer_signature 사용
            logger.warning("기본 infer_signature로 fallback")
            return infer_signature(input_example, output_example)

    def _create_output_example(
        self,
        model: onnx.ModelProto,
        input_example: Union[np.ndarray, dict[str, np.ndarray]],
    ) -> Union[np.ndarray, dict[str, np.ndarray]]:
        """
        ONNX 모델을 실행하여 출력 예제를 생성합니다.

        Args:
            model: ONNX 모델
            input_example: 입력 예제

        Returns:
            Union[np.ndarray, dict[str, np.ndarray]]: 출력 예제

        Raises:
            Exception: 모델 추론 중 오류 발생

        """
        try:
            # ONNX 모델을 바이트로 직렬화
            model_bytes = model.SerializeToString()

            # ONNX Runtime 세션 생성
            session = ort.InferenceSession(
                model_bytes, providers=["CPUExecutionProvider"]
            )

            # 입력 이름 가져오기
            input_names = [input_meta.name for input_meta in session.get_inputs()]

            # 입력 데이터 준비
            if isinstance(input_example, dict):
                # 다중 입력인 경우
                input_dict = {name: input_example[name] for name in input_names}
            else:
                # 단일 입력인 경우
                input_dict = {input_names[0]: input_example}

            # 모델 추론 실행
            outputs = session.run(None, input_dict)

            # 출력 이름 가져오기
            output_names = [output_meta.name for output_meta in session.get_outputs()]

            # 출력 형태 결정
            if len(outputs) == 1:
                # 단일 출력인 경우
                output_example = outputs[0]
                logger.debug(
                    f"단일 출력 예제 생성: 형태={output_example.shape}, 타입={output_example.dtype}"
                )
            else:
                # 다중 출력인 경우
                output_example = dict(zip(output_names, outputs))
                logger.debug(f"다중 출력 예제 생성: {len(outputs)}개 출력")

            return output_example

        except Exception as e:
            logger.error(f"출력 예제 생성 중 오류 발생: {e!s}", exc_info=True)
            # 추론 실패 시 출력 텐서 정보로 더미 출력 생성
            return self._create_dummy_output_example(model)

    def _create_dummy_output_example(
        self, model: onnx.ModelProto
    ) -> Union[np.ndarray, dict[str, np.ndarray]]:
        """
        ONNX 모델의 출력 스키마를 기반으로 더미 출력 예제를 생성합니다.

        Args:
            model: ONNX 모델

        Returns:
            Union[np.ndarray, dict[str, np.ndarray]]: 더미 출력 예제

        """
        try:
            output_tensors = model.graph.output

            if len(output_tensors) == 1:
                # 단일 출력인 경우
                output_tensor = output_tensors[0]
                output_example = self._create_tensor_example(output_tensor)
                logger.debug(f"단일 더미 출력 예제 생성: 형태={output_example.shape}")
                return output_example
            else:
                # 다중 출력인 경우
                output_examples = {}
                for output_tensor in output_tensors:
                    output_name = output_tensor.name
                    output_example = self._create_tensor_example(output_tensor)
                    output_examples[output_name] = output_example
                    logger.debug(
                        f"다중 더미 출력 예제 생성: {output_name}, 형태={output_example.shape}"
                    )

                return output_examples

        except Exception as e:
            logger.error(f"더미 출력 예제 생성 중 오류 발생: {e!s}", exc_info=True)
            # 최후의 수단으로 단순한 배열 반환
            return np.array([0.0])

    def _log_tensor(self, onnx_model: onnx.ModelProto) -> None:
        """
        ONNX 모델의 입력 및 출력 텐서 정보를 로그로 출력합니다.

        Args:
            onnx_model: ONNX 모델

        """
        logger.info("=== ONNX 모델 텐서 정보 ===")

        # 입력 텐서 정보
        logger.info(f"입력 텐서 개수: {len(onnx_model.graph.input)}")
        for i, input_tensor in enumerate(onnx_model.graph.input):
            input_name = input_tensor.name
            input_type = self.get_triton_compatible_type(input_tensor.type.tensor_type)
            input_shape = [
                dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim
            ]

            logger.info(
                f"입력 {i + 1}: 이름={input_name}, 타입={input_type}, 형태={input_shape}"
            )

        # 출력 텐서 정보
        logger.info(f"출력 텐서 개수: {len(onnx_model.graph.output)}")
        for i, output_tensor in enumerate(onnx_model.graph.output):
            output_name = output_tensor.name
            output_type = self.get_triton_compatible_type(
                output_tensor.type.tensor_type
            )
            output_shape = [
                dim.dim_value for dim in output_tensor.type.tensor_type.shape.dim
            ]

            logger.info(
                f"출력 {i + 1}: 이름={output_name}, 타입={output_type}, 형태={output_shape}"
            )

    def _get_numpy_dtype(self, triton_type: str) -> np.dtype:
        """
        Triton 데이터 타입을 NumPy 데이터 타입으로 변환합니다.

        Args:
            triton_type: Triton 호환 데이터 타입 문자열

        Returns:
            np.dtype: NumPy 데이터 타입

        Raises:
            ValueError: 지원되지 않는 데이터 타입

        """
        mapping = {
            "TYPE_BOOL": np.bool_,
            "TYPE_UINT8": np.uint8,
            "TYPE_UINT16": np.uint16,
            "TYPE_UINT32": np.uint32,
            "TYPE_UINT64": np.uint64,
            "TYPE_INT8": np.int8,
            "TYPE_INT16": np.int16,
            "TYPE_INT32": np.int32,
            "TYPE_INT64": np.int64,
            "TYPE_FP16": np.float16,
            "TYPE_FP32": np.float32,
            "TYPE_FP64": np.float64,
            "TYPE_STRING": np.str_,
            # 하위 호환성을 위한 기존 매핑
            "BOOL": np.bool_,
            "UINT8": np.uint8,
            "UINT16": np.uint16,
            "INT32": np.int32,
            "INT64": np.int64,
            "FP16": np.float16,
            "FP32": np.float32,
            "FP64": np.float64,
        }

        result = mapping.get(triton_type)
        if result is None:
            logger.warning(
                f"지원되지 않는 데이터 타입: {triton_type}, FP32로 기본 설정"
            )
            return np.dtype(np.float32)

        return np.dtype(result)
