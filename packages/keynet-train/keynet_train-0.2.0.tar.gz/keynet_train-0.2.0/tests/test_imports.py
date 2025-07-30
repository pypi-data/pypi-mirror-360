"""Simple import tests to verify API changes."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_trace_pytorch_import():
    """Test that trace_pytorch can be imported."""
    from keynet_train import trace_pytorch

    assert callable(trace_pytorch)


def test_log_onnx_model_import():
    """Test that log_onnx_model can be imported."""
    from keynet_train import log_onnx_model

    assert callable(log_onnx_model)


def test_all_exports():
    """Test __all__ exports are correct."""
    import keynet_train

    # Check new functions are in __all__
    assert "trace_pytorch" in keynet_train.__all__
    assert "log_onnx_model" in keynet_train.__all__

    # Check they're accessible
    assert hasattr(keynet_train, "trace_pytorch")
    assert hasattr(keynet_train, "log_onnx_model")


if __name__ == "__main__":
    print("Running import tests...")

    test_trace_pytorch_import()
    print("✓ trace_pytorch import OK")

    test_log_onnx_model_import()
    print("✓ log_onnx_model import OK")

    test_all_exports()
    print("✓ All exports OK")

    print("\nAll import tests passed!")
