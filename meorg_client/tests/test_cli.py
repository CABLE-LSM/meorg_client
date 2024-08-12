from click.testing import CliRunner
import meorg_client.cli as cli
import os
import meorg_client.utilities as mu
from conftest import store
import pytest
import time


@pytest.fixture
def runner() -> CliRunner:
    """Get a runner object.

    Returns
    -------
    click.testing.CliRunner
        Runner object.
    """
    return CliRunner()


@pytest.fixture
def test_filepath() -> str:
    """Get a test filepath from the installation.

    Returns
    -------
    str
        Path to the test filepath.
    """
    return os.path.join(mu.get_installed_data_root(), "test/test.txt")


def test_list_endpoints(runner: CliRunner):
    """Test list-endpoints via CLI."""
    result = runner.invoke(cli.list_endpoints)
    assert result.exit_code == 0


def test_file_upload(runner: CliRunner, test_filepath: str):
    """Test file-upload via CLI."""

    # Upload a tiny test file
    result = runner.invoke(cli.file_upload, [test_filepath])
    assert result.exit_code == 0

    # Add the job_id to the store for the next test
    store.set("file_id", result.output.strip())

    # Let it wait for a short while, allow the server to transfer to object store.
    time.sleep(5)


def test_file_multiple(runner: CliRunner, test_filepath: str):
    """Test file-upload via CLI."""

    # Upload a tiny test file
    result = runner.invoke(cli.file_upload, [test_filepath, test_filepath])
    assert result.exit_code == 0

    # Add the job_id to the store for the next test
    store.set("file_ids", result.output.strip())

    # Let it wait for a short while, allow the server to transfer to object store.
    time.sleep(5)


def test_file_upload_parallel(runner: CliRunner, test_filepath: str):
    """Test file-upload via CLI."""

    # Upload a tiny test file
    result = runner.invoke(
        cli.file_upload_parallel, [test_filepath, test_filepath, "-n 2"]
    )
    assert result.exit_code == 0


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
