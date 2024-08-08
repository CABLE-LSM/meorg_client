"""Test utility functions."""

import meorg_client.utilities as mu
from pathlib import Path


def test_ensure_list():
    """Test ensure_list."""

    # Test null case
    result = mu.ensure_list([1])
    assert isinstance(result, list)

    # Test casting
    result = mu.ensure_list(1)
    assert isinstance(result, list)


def test_get_user_data_filepath():
    """Test get_user_data_filepath."""
    result = mu.get_user_data_filepath("test.txt")
    assert result == Path.home() / ".meorg" / "test.txt"


def test_load_package_data():
    """Test load_package_data."""
    result = mu.load_package_data("openapi.json")
    assert isinstance(result, dict)
