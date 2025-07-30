"""
Unit and regression test for the molmetrics package.
"""

# Import package, test suite, and other packages as needed
import sys

import pytest

import molmetrics


def test_molmetrics_imported():
    """Sample test, will always pass so long as import statement worked."""
    assert "molmetrics" in sys.modules
