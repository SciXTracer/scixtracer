"""Fixtures for testing"""
from pathlib import Path
import pytest

import shutil


@pytest.fixture(scope='package')
def workspace():
    """Create the config file"""
    dir_name = Path(__file__).parent.parent.resolve()
    workspace = dir_name / "workspace"
    return workspace
