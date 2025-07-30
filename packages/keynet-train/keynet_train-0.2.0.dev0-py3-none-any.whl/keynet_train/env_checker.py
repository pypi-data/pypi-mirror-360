import logging
import os

logger = logging.getLogger(__name__)


def check_env_vars(
    required: list | None = None,
):
    """Check if required environment variables are set."""
    if required is None:
        required = [
            "MLFLOW_S3_ENDPOINT_URL",
            "MLFLOW_TRACKING_URI",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "RABBIT_ENDPOINT_URL",
            "RABBIT_MODEL_UPLOAD_TOPIC",
            "TRAIN_ID",
            "MODEL_NAME",
        ]
    missing_vars = [var for var in required if not os.environ.get(var)]

    logger.info("Required environment variables: %s", required)
    if missing_vars:
        error_message = (
            f"다음 환경 변수들이 설정되지 않았습니다: {', '.join(missing_vars)}"
        )
        raise OSError(error_message)
