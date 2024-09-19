"""Test the CLI actions."""

from click.testing import CliRunner
import meorg_client.cli as cli
import os
import meorg_client.utilities as mu
from conftest import store
import pytest


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


@pytest.fixture
def model_output_id() -> str:
    """Get the model output ID out of the environment.

    Returns
    -------
    str
        Model output ID.
    """
    return os.getenv("MEORG_MODEL_OUTPUT_ID")


def test_list_endpoints(runner: CliRunner):
    """Test list-endpoints via CLI.

    Parameters
    ----------
    runner : CliRunner
        Runner object
    """
    result = runner.invoke(cli.list_endpoints)
    assert result.exit_code == 0


def test_file_upload(runner: CliRunner, test_filepath: str, model_output_id: str):
    """Test file-upload via CLI.

    Parameters
    ----------
    runner : CliRunner
        Runner.
    test_filepath : str
        Test filepath.
    model_output_id : str
        Model output ID.
    """
    # Upload a tiny test file
    result = runner.invoke(cli.file_upload, [test_filepath, model_output_id])
    assert result.exit_code == 0

    # Add the job_id to the store for the next test
    store.set("file_id", result.stdout.split()[-1].strip())


def test_file_multiple(runner: CliRunner, test_filepath: str, model_output_id: str):
    """Test file-upload via CLI.

    Parameters
    ----------
    runner : CliRunner
        Runner.
    test_filepath : str
        Test filepath.
    """
    # Upload multiple files
    result = runner.invoke(
        cli.file_upload, [test_filepath, test_filepath, model_output_id]
    )
    assert result.exit_code == 0

    # Add the job_id to the store for the next test
    store.set("file_ids", result.stdout.strip())


def test_file_upload_parallel(
    runner: CliRunner, test_filepath: str, model_output_id: str
):
    """Test file-upload via CLI.

    Parameters
    ----------
    runner : _type_
        Runner.
    model_output_id : str
        Model output ID.
    """
    # Upload multiple files in parallel.
    result = runner.invoke(
        cli.file_upload, [test_filepath, test_filepath, model_output_id, "-n", "2"]
    )
    assert result.exit_code == 0


def test_file_list(runner: CliRunner):
    """Test file-list via CLI.

    Parameters
    ----------
    runner : CliRunner
        Runner.
    """
    result = runner.invoke(cli.file_list, [store.get("model_output_id")])
    assert result.exit_code == 0


def test_delete_file_from_output(runner: CliRunner, model_output_id: str):
    """Test deleting a file from a model output.

    Parameters
    ----------
    runner : CliRunner
        Runner.
    model_output_id : str
        Model output ID.
    """
    # Get the last file added
    file_id = store.get("file_ids").splitlines()[-1]

    # Delete it
    result = runner.invoke(cli.file_delete, [store.get("model_output_id"), file_id])
    assert result.exit_code == 0


def test_delete_all_files_from_output(runner: CliRunner, model_output_id: str):
    """Test deleting all files from a model output.

    Parameters
    ----------
    runner : CliRunner
        Runner.
    model_output_id : str
        Model output ID.
    """

    result = runner.invoke(cli.file_delete_all, [model_output_id])
    assert result.exit_code == 0
