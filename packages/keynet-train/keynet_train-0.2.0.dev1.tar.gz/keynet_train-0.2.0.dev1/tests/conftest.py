"""Shared test configuration and fixtures."""

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def setup_env():
    """Setup environment variables for testing."""
    # Set test environment variables
    os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///test_mlflow.db"
    os.environ["KEYNET_ENV"] = "test"

    # Disable MLflow autologging by default
    os.environ["MLFLOW_AUTOLOG_DISABLE"] = "true"

    yield

    # Cleanup
    if Path("test_mlflow.db").exists():
        Path("test_mlflow.db").unlink()


@pytest.fixture
def disable_network():
    """Disable network calls for unit tests."""
    import socket

    old_socket = socket.socket

    def guard(*args, **kwargs):
        raise Exception("Network access not allowed in tests")

    socket.socket = guard
    yield
    socket.socket = old_socket
