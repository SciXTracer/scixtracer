"""Fixtures for testing"""
from pathlib import Path
import pytest


@pytest.fixture(scope='package')
def workspace():
    """Create the config file"""
    dir_name = Path(__file__).parent.parent.resolve()
    return dir_name / "workspace"
