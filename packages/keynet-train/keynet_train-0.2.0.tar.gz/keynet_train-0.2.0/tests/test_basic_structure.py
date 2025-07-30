"""Basic structural tests without imports."""

import ast
import json
from pathlib import Path


def test_package_structure():
    """Test basic package structure."""
    train_dir = Path(__file__).parent.parent

    # Check required files exist
    required_files = [
        "keynet_train/__init__.py",
        "keynet_train/annotation.py",
        "keynet_train/onnx_client.py",
        "keynet_train/base_mlflow_client.py",
        "pyproject.toml",
        "README.md",
    ]

    for file in required_files:
        assert (train_dir / file).exists(), f"Missing file: {file}"

    print("✓ Package structure is correct")


def test_pyproject_toml():
    """Test pyproject.toml configuration."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()

    # Check package name
    assert 'name = "keynet-train"' in content

    # Check NumPy version constraint
    assert "numpy>=1.25.0,<2.0" in content, "NumPy should be constrained to <2.0"

    # Check other key dependencies
    assert "mlflow" in content
    assert "torch" in content
    assert "onnx" in content
    assert "onnxruntime" in content

    print("✓ pyproject.toml is correctly configured")


def test_function_signatures():
    """Test function signatures without importing."""
    annotation_path = Path(__file__).parent.parent / "keynet_train" / "annotation.py"
    tree = ast.parse(annotation_path.read_text())

    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = {
                "args": [arg.arg for arg in node.args.args],
                "defaults": len(node.args.defaults),
                "returns": bool(node.returns),
                "docstring": ast.get_docstring(node) is not None,
            }

    # Check trace_pytorch
    assert "trace_pytorch" in functions
    tp = functions["trace_pytorch"]
    assert "experiment_name" in tp["args"]
    assert "sample_input" in tp["args"]
    assert "dynamic_axes" in tp["args"]
    assert tp["docstring"]

    # Check log_onnx_model
    assert "log_onnx_model" in functions
    lom = functions["log_onnx_model"]
    assert "experiment_name" in lom["args"]
    assert "onnx_model_path" in lom["args"]
    assert "metadata" in lom["args"]
    assert lom["docstring"]

    print("✓ Function signatures are correct")


def test_docstring_content():
    """Test that docstrings contain key information."""
    annotation_path = Path(__file__).parent.parent / "keynet_train" / "annotation.py"
    content = annotation_path.read_text()

    # Find trace_pytorch docstring
    trace_start = content.find("def trace_pytorch")
    trace_doc_start = content.find('"""', trace_start)
    trace_doc_end = content.find('"""', trace_doc_start + 3)
    trace_doc = content[trace_doc_start:trace_doc_end]

    # Check trace_pytorch documentation
    assert "PyTorch" in trace_doc
    assert "MLflow" in trace_doc
    assert "@trace_pytorch" in trace_doc or "사용 예시" in trace_doc

    # Find log_onnx_model docstring
    log_start = content.find("def log_onnx_model")
    log_doc_start = content.find('"""', log_start)
    log_doc_end = content.find('"""', log_doc_start + 3)
    log_doc = content[log_doc_start:log_doc_end]

    # Check log_onnx_model documentation
    assert "프레임워크 독립적" in log_doc
    assert "ONNX" in log_doc
    assert any(fw in log_doc for fw in ["TensorFlow", "JAX", "MXNet"])

    print("✓ Docstrings contain proper information")


def test_readme_examples():
    """Test that README contains proper examples."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()

    # Check for PyTorch example
    assert "@trace_pytorch" in content
    assert "torch.randn" in content

    # Check for framework-agnostic example
    assert "log_onnx_model" in content
    assert "tensorflow" in content.lower()
    assert "tf2onnx" in content

    # Check for key features
    assert "프레임워크 독립적" in content
    assert "Dynamic Axes" in content or "dynamic_axes" in content

    print("✓ README contains proper examples")


def generate_test_report():
    """Generate a simple test report."""
    report = {
        "test_suite": "keynet-train API changes",
        "changes": {
            "renamed": {"@trace": "@trace_pytorch", "reason": "명확한 프레임워크 표시"},
            "added": {
                "log_onnx_model": "프레임워크 독립적 ONNX 모델 배포",
                "dynamic_axes": "@trace_pytorch에 동적 차원 지원 추가",
            },
            "compatibility": {
                "backward": "제거됨 (불필요)",
                "numpy": "< 2.0으로 제한 (onnxruntime 호환성)",
            },
        },
        "test_status": "PASSED",
    }

    print("\n📊 Test Report:")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("Running basic structure tests...\n")

    try:
        test_package_structure()
        test_pyproject_toml()
        test_function_signatures()
        test_docstring_content()
        test_readme_examples()

        generate_test_report()

        print("\n✅ All basic tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
