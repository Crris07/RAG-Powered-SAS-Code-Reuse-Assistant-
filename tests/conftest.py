"""conftest - pytest configuration"""

import pytest
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_data_path():
    """Get test data directory"""
    return project_root / "tests" / "fixtures"
