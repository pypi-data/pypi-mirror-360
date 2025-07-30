"""Tests for annotation module (trace_pytorch and log_onnx_model)."""

import tempfile
from pathlib import Path
from unittest.mock import patch

# Import mlflow modules explicitly before keynet_train
import mlflow
import mlflow.onnx
import mlflow.pytorch
import pytest
import torch
import torch.nn as nn

from keynet_train import log_onnx_model, trace_pytorch


class SimpleModel(nn.Module):
    """Simple test model."""

    def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
        """Initialize simple model."""
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


class MultiInputModel(nn.Module):
    """Model with multiple inputs."""

    def __init__(self):
        """Initialize multi-input model."""
        super().__init__()
        self.image_branch = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        self.mask_branch = nn.Sequential(
            nn.Conv2d(1, 8, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
        )
        self.fc = nn.Linear(24, 10)

    def forward(self, image, mask):
        img_features = self.image_branch(image)
        mask_features = self.mask_branch(mask)
        combined = torch.cat([img_features, mask_features], dim=1)
        return self.fc(combined)


@pytest.fixture
def setup_mlflow():
    """Setup MLflow for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mlflow.set_tracking_uri(f"file://{tmpdir}")
        yield tmpdir


@pytest.fixture
def mock_onnx_client():
    """Mock OnnxClient for testing."""
    with patch("keynet_train.annotation.onnx_client") as mock_client:
        mock_client.upload.return_value = "mocked/upload/path"
        yield mock_client


class TestTracePytorch:
    """Tests for trace_pytorch decorator."""

    def test_basic_trace_pytorch(self, setup_mlflow, mock_onnx_client):
        """Test basic trace_pytorch functionality."""

        @trace_pytorch(
            "test_experiment",
            torch.randn(1, 784),
            auto_convert_onnx=True,
            enable_autolog=False,
        )
        def train_simple_model():
            model = SimpleModel()
            # Simulate training
            mlflow.log_metric("test_metric", 0.95)
            return model

        # Execute the decorated function
        model = train_simple_model()

        # Verify model is returned
        assert isinstance(model, SimpleModel)

        # Verify MLflow experiment was created
        experiment = mlflow.get_experiment_by_name("test_experiment")
        assert experiment is not None

        # Verify ONNX conversion was called
        assert mock_onnx_client.upload.called

    def test_multi_input_model(self, setup_mlflow, mock_onnx_client):
        """Test trace_pytorch with multiple inputs."""
        sample_inputs = {
            "image": torch.randn(1, 3, 32, 32),
            "mask": torch.randn(1, 1, 32, 32),
        }

        @trace_pytorch(
            "multi_input_experiment",
            sample_inputs,
            auto_convert_onnx=True,
            enable_autolog=False,
        )
        def train_multi_input():
            return MultiInputModel()

        model = train_multi_input()
        assert isinstance(model, MultiInputModel)
        assert mock_onnx_client.upload.called

    def test_dynamic_axes(self, setup_mlflow, mock_onnx_client):
        """Test trace_pytorch with dynamic axes."""
        dynamic_axes = {
            "input_0": {0: "batch_size", 1: "sequence_length"},
            "output_0": {0: "batch_size"},
        }

        @trace_pytorch(
            "dynamic_axes_experiment",
            torch.randn(1, 10, 128),  # [batch, seq_len, hidden]
            dynamic_axes=dynamic_axes,
            auto_convert_onnx=True,
            enable_autolog=False,
        )
        def train_dynamic_model():
            model = nn.LSTM(128, 64, batch_first=True)
            return model

        model = train_dynamic_model()
        assert isinstance(model, nn.LSTM)

    def test_invalid_return_type(self, setup_mlflow):
        """Test that non-Module return raises error."""

        @trace_pytorch(
            "invalid_experiment",
            torch.randn(1, 784),
            enable_autolog=False,
        )
        def train_invalid():
            model = SimpleModel()
            return model, 0.95  # Invalid: returning tuple

        with pytest.raises(ValueError, match="torch.nn.Module"):
            train_invalid()

    def test_device_handling(self, setup_mlflow, mock_onnx_client):
        """Test device handling (CPU/CUDA)."""

        @trace_pytorch(
            "device_experiment",
            torch.randn(1, 784),
            device="cpu",  # Force CPU even if CUDA available
            auto_convert_onnx=True,
            enable_autolog=False,
        )
        def train_on_cpu():
            return SimpleModel()

        model = train_on_cpu()
        # Check model is on CPU
        assert next(model.parameters()).device.type == "cpu"


class TestLogOnnxModel:
    """Tests for log_onnx_model function."""

    def test_basic_onnx_logging(self, setup_mlflow, mock_onnx_client):
        """Test basic ONNX model logging."""
        # Create a simple ONNX model
        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = Path(tmpdir) / "test_model.onnx"

            # Create and save a simple PyTorch model as ONNX
            model = SimpleModel()
            dummy_input = torch.randn(1, 784)
            torch.onnx.export(
                model,
                dummy_input,
                str(onnx_path),
                input_names=["input"],
                output_names=["output"],
                dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
            )

            # Test log_onnx_model
            result = log_onnx_model(
                experiment_name="onnx_experiment",
                onnx_model_path=onnx_path,
                metadata={"framework": "pytorch", "version": "1.0"},
            )

            assert result == "mocked/upload/path"
            assert mock_onnx_client.upload.called

            # Verify experiment was created
            experiment = mlflow.get_experiment_by_name("onnx_experiment")
            assert experiment is not None

    def test_with_signature(self, setup_mlflow, mock_onnx_client):
        """Test ONNX logging with custom signature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            onnx_path = Path(tmpdir) / "model_with_sig.onnx"

            # Create ONNX model
            model = SimpleModel()
            dummy_input = torch.randn(2, 784)
            torch.onnx.export(model, dummy_input, str(onnx_path))

            # Create signature
            from mlflow.models.signature import infer_signature

            numpy_input = dummy_input.numpy()
            numpy_output = model(dummy_input).detach().numpy()
            signature = infer_signature(numpy_input, numpy_output)

            # Log with signature
            result = log_onnx_model(
                experiment_name="sig_experiment",
                onnx_model_path=onnx_path,
                signature=signature,
                input_example=numpy_input,
            )

            assert result == "mocked/upload/path"

    def test_nonexistent_file(self, setup_mlflow):
        """Test error handling for non-existent ONNX file."""
        with pytest.raises(FileNotFoundError):
            log_onnx_model(
                experiment_name="error_experiment",
                onnx_model_path="nonexistent.onnx",
            )

    def test_tensorflow_example(self, setup_mlflow, mock_onnx_client):
        """Test TensorFlow-like workflow (simulated)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Simulate TensorFlow model converted to ONNX
            onnx_path = Path(tmpdir) / "tf_model.onnx"

            # Create a dummy ONNX model to simulate TF conversion
            model = nn.Sequential(
                nn.Flatten(),
                nn.Linear(784, 128),
                nn.ReLU(),
                nn.Linear(128, 10),
            )
            dummy_input = torch.randn(1, 28, 28)
            torch.onnx.export(model, dummy_input, str(onnx_path))

            # Log as if it were from TensorFlow
            result = log_onnx_model(
                experiment_name="tensorflow_experiment",
                onnx_model_path=onnx_path,
                model_name="mnist_classifier",
                metadata={
                    "framework": "tensorflow",
                    "tf_version": "2.13.0",
                    "model_type": "classification",
                    "dataset": "mnist",
                },
            )

            assert result == "mocked/upload/path"
            assert mock_onnx_client.upload.called


class TestIntegration:
    """Integration tests for the full workflow."""

    def test_pytorch_to_onnx_full_workflow(self, setup_mlflow, mock_onnx_client):
        """Test complete PyTorch training to ONNX deployment workflow."""

        @trace_pytorch(
            "integration_experiment",
            torch.randn(2, 784),
            run_name="integration_test",
            auto_convert_onnx=True,
            log_model_info=True,
            enable_autolog=False,
        )
        def full_training_workflow():
            model = SimpleModel()

            # Simulate training metrics
            for epoch in range(3):
                mlflow.log_metric("loss", 1.0 / (epoch + 1), step=epoch)
                mlflow.log_metric("accuracy", 0.8 + 0.05 * epoch, step=epoch)

            # Log parameters
            mlflow.log_params(
                {
                    "learning_rate": 0.001,
                    "batch_size": 32,
                    "epochs": 3,
                }
            )

            return model

        model = full_training_workflow()

        # Verify model and ONNX upload
        assert isinstance(model, SimpleModel)
        assert mock_onnx_client.upload.called

        # Check that run exists and has expected tags/params
        runs = mlflow.search_runs(
            experiment_names=["integration_experiment"],
            filter_string="tags.mlflow.runName = 'integration_test'",
        )
        assert len(runs) == 1

    def test_framework_agnostic_workflow(self, setup_mlflow, mock_onnx_client):
        """Test framework-agnostic ONNX workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Step 1: Create ONNX model (simulating export from any framework)
            onnx_path = Path(tmpdir) / "agnostic_model.onnx"

            # Create a model that could come from any framework
            model = nn.Sequential(
                nn.Conv2d(3, 32, 3),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d(1),
                nn.Flatten(),
                nn.Linear(32, 10),
            )
            dummy_input = torch.randn(1, 3, 32, 32)
            torch.onnx.export(
                model,
                dummy_input,
                str(onnx_path),
                input_names=["image"],
                output_names=["logits"],
            )

            # Step 2: Log the ONNX model as if from JAX
            result = log_onnx_model(
                experiment_name="jax_experiment",
                onnx_model_path=onnx_path,
                run_name="jax_cnn_model",
                model_name="image_classifier",
                metadata={
                    "framework": "jax",
                    "library": "flax",
                    "architecture": "SimpleCNN",
                    "num_classes": 10,
                },
            )

            assert result == "mocked/upload/path"

            # Verify the run was created with correct metadata
            runs = mlflow.search_runs(
                experiment_names=["jax_experiment"],
                filter_string="tags.mlflow.runName = 'jax_cnn_model'",
            )
            assert len(runs) == 1
            assert runs.iloc[0]["params.framework"] == "jax"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
