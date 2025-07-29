"""pytest-reqcov: A pytest plugin for requirement coverage tracking."""

__version__ = "0.2.0"
__author__ = "Miquel Garcia"
__email__ = "miquel@mgfernan.com"

from .plugin import pytest_addoption, pytest_collection_modifyitems, pytest_runtest_makereport, pytest_sessionfinish

__all__ = ["pytest_addoption", "pytest_collection_modifyitems", "pytest_runtest_makereport", "pytest_sessionfinish"]
