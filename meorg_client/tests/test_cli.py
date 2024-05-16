from click.testing import CliRunner
import meorg_client.cli as cli
import os
import meorg_client.utilities as mu
from conftest import store
import pytest
import time


@pytest.fixture
def runner():
    return CliRunner()


def test_list_endpoints(runner):
    """Test list-endpoints via CLI."""
    result = runner.invoke(cli.list_endpoints)
    assert result.exit_code == 0


def test_file_upload(runner):
    """Test file-upload via CLI."""

    # Upload a tiny test file
    filepath = os.path.join(mu.get_installed_data_root(), "test/test.txt")
    result = runner.invoke(cli.file_upload, [filepath])
    assert result.exit_code == 0

    # Add the job_id to the store for the next test
    store.set("job_id", result.output.strip())

    # Let it wait for a short while, allow the server to transfer to object store.
    time.sleep(5)


def test_file_status(runner):
    """Test file-status via CLI."""

    # Get the file ID based on the job ID
    job_id = store.get("job_id")
    result = runner.invoke(cli.file_status, [job_id])
    assert result.exit_code == 0
    assert result.output != "Pending"

    # Add file_id to the store for the next test
    store.set("file_id", result.output.strip())


def test_file_list(runner):
    """Test file-list via CLI."""
    result = runner.invoke(cli.file_list, [store.get("model_output_id")])
    assert result.exit_code == 0


def test_file_attach(runner):
    """Test file-attach via CLI."""

    result = runner.invoke(
        cli.file_attach, [store.get("file_id"), store.get("model_output_id")]
    )

    assert result.exit_code == 0
