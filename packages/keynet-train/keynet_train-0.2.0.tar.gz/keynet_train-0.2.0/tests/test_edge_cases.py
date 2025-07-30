"""Edge case tests for trace_pytorch and log_onnx_model."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import mlflow
import pytest
import torch
import torch.nn as nn

from keynet_train import log_onnx_model, trace_pytorch


@pytest.fixture
def setup_mlflow():
    """Setup MLflow for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mlflow.set_tracking_uri(f"file://{tmpdir}")
        yield tmpdir


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_trace_pytorch_no_cuda(self, setup_mlflow):
        """Test trace_pytorch when CUDA is requested but not available."""
        with patch("torch.cuda.is_available", return_value=False):

            @trace_pytorch(
                "no_cuda_exp",
                torch.randn(1, 10),
                device="cuda",  # Request CUDA
                enable_autolog=False,
            )
            def train_model():
                return nn.Linear(10, 5)

            # Should fall back to CPU without error
            with patch("keynet_train.annotation.onnx_client"):
                model = train_model()
                assert next(model.parameters()).device.type == "cpu"

    def test_empty_metadata(self, setup_mlflow):
        """Test log_onnx_model with empty metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal ONNX file
            onnx_path = Path(tmpdir) / "minimal.onnx"
            model = nn.Linear(5, 3)
            torch.onnx.export(model, torch.randn(1, 5), str(onnx_path))

            with patch("keynet_train.annotation.onnx_client") as mock_client:
                mock_client.upload.return_value = "path"

                # Should work with no metadata
                result = log_onnx_model(
                    experiment_name="minimal_exp",
                    onnx_model_path=onnx_path,
                    metadata=None,  # No metadata
                )

                assert result is not None

    def test_large_model_name(self, setup_mlflow):
        """Test handling of very long model names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use a reasonably long name that won't exceed OS limits
            long_name = "very_" * 20 + "long_model_name.onnx"
            onnx_path = Path(tmpdir) / long_name

            model = nn.Linear(10, 10)
            torch.onnx.export(model, torch.randn(1, 10), str(onnx_path))

            with patch("keynet_train.annotation.onnx_client") as mock_client:
                mock_client.upload.return_value = "path"

                # Should handle long names gracefully
                result = log_onnx_model(
                    experiment_name="long_name_exp",
                    onnx_model_path=onnx_path,
                )

                assert result is not None

    def test_special_characters_in_experiment_name(self, setup_mlflow):
        """Test experiment names with special characters."""

        @trace_pytorch(
            "experiment-with-dashes_and_underscores",
            torch.randn(1, 10),
            enable_autolog=False,
        )
        def train_model():
            return nn.Linear(10, 5)

        with patch("keynet_train.annotation.onnx_client"):
            # Should handle special chars in experiment name
            model = train_model()
            assert model is not None

    def test_onnx_conversion_fallback(self, setup_mlflow):
        """Test ONNX conversion fallback mechanisms."""

        class ComplexModel(nn.Module):
            """Model that might be tricky to convert."""

            def __init__(self):
                """Initialize complex model."""
                super().__init__()
                self.lstm = nn.LSTM(10, 20, batch_first=True)
                self.fc = nn.Linear(20, 5)

            def forward(self, x):
                # LSTM can be tricky for ONNX
                out, _ = self.lstm(x)
                return self.fc(out[:, -1, :])

        @trace_pytorch(
            "complex_model_exp",
            torch.randn(1, 5, 10),  # [batch, seq, features]
            enable_autolog=False,
            onnx_opset_version=11,  # Older opset
        )
        def train_complex():
            return ComplexModel()

        with patch("keynet_train.annotation.onnx_client"):
            # Should handle complex models
            model = train_complex()
            assert isinstance(model, ComplexModel)

    def test_interrupted_upload(self, setup_mlflow):
        """Test handling of interrupted ONNX upload."""

        @trace_pytorch(
            "interrupt_exp",
            torch.randn(1, 10),
            enable_autolog=False,
        )
        def train_model():
            return nn.Linear(10, 5)

        with patch("keynet_train.annotation.onnx_client") as mock_client:
            # Simulate upload failure
            mock_client.upload.side_effect = Exception("Network error")

            # Should still return model even if upload fails
            model = train_model()
            assert isinstance(model, nn.Linear)

    def test_invalid_dynamic_axes(self, setup_mlflow):
        """Test handling of invalid dynamic axes configuration."""
        # Invalid: referring to non-existent tensor names
        invalid_dynamic_axes = {
            "nonexistent_input": {0: "batch"},
            "also_invalid": {0: "batch"},
        }

        @trace_pytorch(
            "invalid_axes_exp",
            torch.randn(1, 10),
            dynamic_axes=invalid_dynamic_axes,
            enable_autolog=False,
        )
        def train_model():
            return nn.Linear(10, 5)

        with patch("keynet_train.annotation.onnx_client"):
            # Should handle invalid axes gracefully
            model = train_model()
            assert model is not None


class TestConcurrency:
    """Test concurrent execution scenarios."""

    def test_multiple_experiments_simultaneously(self, setup_mlflow):
        """Test running multiple experiments at once."""
        import threading

        results = {}
        errors = []

        def run_experiment(exp_name, idx):
            try:

                @trace_pytorch(
                    exp_name,
                    torch.randn(1, 10),
                    enable_autolog=False,
                )
                def train():
                    return nn.Linear(10, 5)

                with patch("keynet_train.annotation.onnx_client"):
                    model = train()
                    results[idx] = model
            except Exception as e:
                errors.append(e)

        # Run multiple experiments in parallel
        threads = []
        for i in range(5):
            t = threading.Thread(target=run_experiment, args=(f"concurrent_exp_{i}", i))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # All should succeed
        assert len(errors) == 0
        assert len(results) == 5
