"""Tests for utility functions in annotation module."""

import torch
from mlflow.models.signature import infer_signature

from keynet_train.annotation import (
    _convert_to_numpy,
    _generate_input_output_names,
    _infer_model_schema,
)


class TestConvertToNumpy:
    """Tests for _convert_to_numpy function."""

    def test_single_tensor(self):
        """Test converting single tensor."""
        tensor = torch.randn(2, 3)
        numpy_arr = _convert_to_numpy(tensor)
        assert numpy_arr.shape == (2, 3)
        assert hasattr(numpy_arr, "dtype")

    def test_dict_of_tensors(self):
        """Test converting dictionary of tensors."""
        tensor_dict = {
            "input1": torch.randn(1, 10),
            "input2": torch.randn(1, 20),
        }
        numpy_dict = _convert_to_numpy(tensor_dict)

        assert isinstance(numpy_dict, dict)
        assert "input1" in numpy_dict
        assert "input2" in numpy_dict
        assert numpy_dict["input1"].shape == (1, 10)
        assert numpy_dict["input2"].shape == (1, 20)

    def test_nested_structures(self):
        """Test converting nested structures."""
        nested = {
            "tensors": [torch.randn(1, 5), torch.randn(1, 5)],
            "single": torch.randn(2, 2),
        }
        numpy_nested = _convert_to_numpy(nested)

        assert isinstance(numpy_nested["tensors"], list)
        assert len(numpy_nested["tensors"]) == 2
        assert numpy_nested["single"].shape == (2, 2)


class TestGenerateInputOutputNames:
    """Tests for _generate_input_output_names function."""

    def test_single_input_output(self):
        """Test name generation for single input/output."""
        # Create a simple signature
        input_data = torch.randn(1, 10).numpy()
        output_data = torch.randn(1, 5).numpy()
        signature = infer_signature(input_data, output_data)

        input_names, output_names = _generate_input_output_names(signature)

        assert len(input_names) >= 1
        assert len(output_names) >= 1
        assert input_names[0].startswith("input")
        assert output_names[0].startswith("output")

    def test_dict_input_names(self):
        """Test name generation with dictionary inputs."""
        # Create signature with named inputs
        input_data = {"image": torch.randn(1, 3, 32, 32).numpy()}
        output_data = torch.randn(1, 10).numpy()
        signature = infer_signature(input_data, output_data)

        input_names, output_names = _generate_input_output_names(signature)

        # Should preserve dictionary keys as names
        assert "image" in input_names or input_names[0] == "input_0"
        assert len(output_names) >= 1


class TestInferModelSchema:
    """Tests for _infer_model_schema function."""

    def test_simple_model_schema(self):
        """Test schema inference for simple model."""
        model = torch.nn.Linear(10, 5)
        sample_input = torch.randn(2, 10)

        signature = _infer_model_schema(model, sample_input)

        assert signature is not None
        assert hasattr(signature, "inputs")
        assert hasattr(signature, "outputs")

    def test_multi_input_model_schema(self):
        """Test schema inference for multi-input model."""

        class MultiInputModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.fc1 = torch.nn.Linear(10, 5)
                self.fc2 = torch.nn.Linear(20, 5)

            def forward(self, x1, x2):
                return self.fc1(x1) + self.fc2(x2)

        model = MultiInputModel()
        sample_inputs = {
            "x1": torch.randn(1, 10),
            "x2": torch.randn(1, 20),
        }

        signature = _infer_model_schema(model, sample_inputs)

        assert signature is not None
