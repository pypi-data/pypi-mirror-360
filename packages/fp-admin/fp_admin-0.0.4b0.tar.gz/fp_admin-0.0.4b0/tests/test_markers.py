"""
Test to verify that pytest markers are working correctly.
"""

import pytest


@pytest.mark.unit
def test_unit_marker() -> None:
    """Test that unit marker works."""
    assert True


@pytest.mark.integration
def test_integration_marker() -> None:
    """Test that integration marker works."""
    assert True


@pytest.mark.e2e
def test_e2e_marker() -> None:
    """Test that e2e marker works."""
    assert True


@pytest.mark.slow
def test_slow_marker() -> None:
    """Test that slow marker works."""
    assert True


def test_no_marker() -> None:
    """Test without any marker."""
    assert True
