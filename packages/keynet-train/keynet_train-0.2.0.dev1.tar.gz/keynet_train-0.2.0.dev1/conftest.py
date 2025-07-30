"""Root conftest.py for proper test module initialization."""

import sys
from pathlib import Path

# Add the package directory to Python path
package_dir = Path(__file__).parent
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))

# Import torch early to ensure proper initialization
import torch  # noqa: E402

# Ensure CUDA availability is properly initialized
_ = torch.cuda.is_available()
