import logging
from typing import Optional, Union

import mlflow
import numpy as np
import torch
from deprecated import deprecated

from .base_mlflow_client import BaseMLflowClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@deprecated(reason="Use OnnxClient instead")
class TorchClient(BaseMLflowClient):
    def upload(
        self,
        model: torch.nn.Module,
        input_example: Optional[Union[torch.Tensor, np.ndarray]] = None,
    ):
        """
        PyTorch 모델을 MLflow에 업로드합니다.

        Args:
            model: PyTorch 모델
            input_example: 자동 signature 추론을 위한 입력 예제

        """
        try:
            logger.info("PyTorch 모델 업로드 시작")

            # 입력 예제가 제공되지 않은 경우 기본값 생성
            if input_example is None:
                logger.warning(
                    "입력 예제가 제공되지 않았습니다. 기본 입력 예제를 생성합니다."
                )
                input_example = torch.randn(1, 3, 224, 224)  # 일반적인 이미지 크기

            # numpy array로 변환
            if isinstance(input_example, torch.Tensor):
                input_example = input_example.detach().cpu().numpy()

            self._log_tensor(model, input_example)
            path = self._log_model(model=model, input_example=input_example)

            if not self.is_production:
                logger.info("개발 모드: RabbitMQ 메시지 전송 건너뜀")
                return path

            self._publish_to_rabbitmq(path)
            return path

        except Exception as e:
            logger.error(f"PyTorch 모델 업로드 중 오류 발생: {e!s}", exc_info=True)
            raise

    def _publish_to_rabbitmq(self, path: str) -> None:
        """RabbitMQ에 모델 업로드 메시지를 발행합니다."""
        import json

        channel = self.get_connection().channel()
        message = json.dumps(
            {"train_id": self.train_id, "full_path": path}, ensure_ascii=False
        )

        try:
            channel.basic_publish(
                exchange=self._uploadModelExchange,
                routing_key=self._uploadModelExchange,
                body=message,
            )
            logger.info(f"RabbitMQ에 모델 업로드 완료: {message}")
        except Exception as e:
            logger.error(f"RabbitMQ 메시지 발행 실패: {e!s}", exc_info=True)
            raise
        finally:
            channel.close()

    def _log_tensor(self, model: torch.nn.Module, input_example: np.ndarray = None):
        """모델의 텐서 정보를 로그로 출력합니다."""
        hooks = []

        def register_hook(module):
            def hook(module, input, output):
                print(f"{module.__class__.__name__}:")
                if hasattr(input[0], "size"):
                    print(f"  Input Shape: {list(input[0].size())}")
                if hasattr(output, "size"):
                    print(f"  Output Shape: {list(output.size())}")
                if hasattr(output, "dtype"):
                    print(f"  Data Type: {output.dtype}")

            # Check if it's a layer with parameters; skip for non-layer modules
            if list(module.children()) == []:  # Leaf module, e.g., Conv2d, Linear
                hooks.append(module.register_forward_hook(hook))

        # Apply the hook to all the layers
        model.apply(register_hook)

        # Dummy forward pass to trigger the hooks
        if input_example is not None:
            with torch.no_grad():
                if isinstance(input_example, np.ndarray):
                    input_tensor = torch.from_numpy(input_example).float()
                else:
                    input_tensor = input_example
                model(input_tensor)

        # Remove hooks to clean up
        for hook in hooks:
            hook.remove()

    def _log_model(self, model: torch.nn.Module, input_example: np.ndarray) -> str:
        """MLflow에 모델을 로깅합니다."""
        try:
            # 최신 MLflow 3.11.1 방식: input_example을 사용하여 자동 signature 추론
            mlflow.pytorch.log_model(
                pytorch_model=model,
                artifact_path=self.model_name,
                input_example=input_example,  # 자동 signature 추론
            )

            artifact_uri = mlflow.get_artifact_uri()
            model_full_path = f"{artifact_uri}/{self.model_name}"

            logger.info(f"MLflow에 모델 저장 완료: {model_full_path}")
            return model_full_path
        except Exception as e:
            logger.error(f"모델 로깅 중 오류 발생: {e!s}", exc_info=True)
            raise
