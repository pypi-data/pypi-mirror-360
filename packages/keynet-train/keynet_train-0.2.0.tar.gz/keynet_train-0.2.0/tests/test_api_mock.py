"""Mock tests for API verification without actual imports."""

import ast
from pathlib import Path


def parse_file(filepath):
    """Parse a Python file and return AST."""
    return ast.parse(Path(filepath).read_text())


def test_annotation_file_has_new_functions():
    """Verify annotation.py has the new functions."""
    annotation_path = Path(__file__).parent.parent / "keynet_train" / "annotation.py"
    tree = parse_file(annotation_path)

    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    # Check new function names
    assert "trace_pytorch" in functions, "trace_pytorch not found in annotation.py"
    assert "log_onnx_model" in functions, "log_onnx_model not found in annotation.py"

    # Old trace should NOT exist as a function (it's an alias in __init__.py)
    assert "trace" not in functions, "Old 'trace' function should be renamed"

    print("✓ annotation.py has correct functions")


def test_init_file_exports():
    """Verify __init__.py exports the right symbols."""
    init_path = Path(__file__).parent.parent / "keynet_train" / "__init__.py"
    tree = parse_file(init_path)

    # Find imports - check all ImportFrom nodes
    imported_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imported_names.add(alias.name)

    # Check imports
    assert "trace_pytorch" in imported_names, "trace_pytorch not imported"
    assert "log_onnx_model" in imported_names, "log_onnx_model not imported"

    # Find __all__ definition
    all_items = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__" and isinstance(node.value, ast.List):
                        all_items = [
                            elt.s for elt in node.value.elts if isinstance(elt, ast.Str)
                        ] or [
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        ]

    # Check __all__ exports
    assert "trace_pytorch" in all_items, "trace_pytorch not in __all__"
    assert "log_onnx_model" in all_items, "log_onnx_model not in __all__"

    print("✓ __init__.py exports are correct")


def test_readme_updated():
    """Verify README.md is updated with new API."""
    readme_path = Path(__file__).parent.parent / "README.md"
    content = readme_path.read_text()

    # Check for new function names
    assert "trace_pytorch" in content, "README should mention trace_pytorch"
    assert "log_onnx_model" in content, "README should mention log_onnx_model"

    # Check for TensorFlow example
    assert "tensorflow" in content.lower(), "README should have TensorFlow example"
    assert "tf2onnx" in content, "README should show tf2onnx usage"

    # Check that @trace_pytorch is used
    assert "@trace_pytorch(" in content, "README should use @trace_pytorch decorator"

    print("✓ README.md is updated")


def test_log_onnx_model_signature():
    """Verify log_onnx_model has correct signature."""
    annotation_path = Path(__file__).parent.parent / "keynet_train" / "annotation.py"
    tree = parse_file(annotation_path)

    # Find log_onnx_model function
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "log_onnx_model"):
            continue
        # Check parameters
        args = [arg.arg for arg in node.args.args]
        expected_args = [
            "experiment_name",
            "onnx_model_path",
            "run_name",
            "model_name",
            "signature",
            "input_example",
            "metadata",
        ]
        for expected in expected_args:
            assert expected in args, f"Parameter {expected} not found"

        # Check it returns Optional[str]
        if node.returns:
            assert "Optional" in ast.unparse(node.returns)

        print("✓ log_onnx_model signature is correct")
        break


def test_dynamic_axes_parameter():
    """Verify trace_pytorch has dynamic_axes parameter."""
    annotation_path = Path(__file__).parent.parent / "keynet_train" / "annotation.py"
    tree = parse_file(annotation_path)

    # Find trace_pytorch function
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "trace_pytorch":
            # Check parameters
            args = [arg.arg for arg in node.args.args]
            assert "dynamic_axes" in args, "dynamic_axes parameter not found"

            print("✓ trace_pytorch has dynamic_axes parameter")
            break


if __name__ == "__main__":
    print("Running API verification tests...\n")

    test_annotation_file_has_new_functions()
    test_init_file_exports()
    test_readme_updated()
    test_log_onnx_model_signature()
    test_dynamic_axes_parameter()

    print("\n✅ All API tests passed!")
