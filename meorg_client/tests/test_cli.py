"""Test the CLI actions."""

from click.testing import CliRunner
import meorg_client.cli as cli
import os
import meorg_client.utilities as mu
import pytest
from conftest import phase_report_key


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
def model_output_generator(request, runner: CliRunner, model_profile_id: str):
    """A generator function for creating new model outputs before running a test.

       After the test has run, automatically deletes all model outputs created within
       the test

    Parameters
    -------
    request:
        Request object by pytest

    click.testing.CliRunner
        Runner object.

    model_profile_id
        Model profile ID.
    """
    model_output_ids = []

    def _make_model_output(model_output_name):
        """Create new model output ID.

        Parameters
        -------
        name:
            Model output name
        """
        # `model_profile_id` from `model_output_generator`
        result = runner.invoke(
            cli.create_new_model_output,
            [model_profile_id, model_output_name],
            standalone_mode=False,
        )
        assert result.exit_code == 0
        model_output_id = result.return_value
        model_output_ids.append(model_output_id)
        return model_output_id

    yield _make_model_output

    # If using tests like model_output_delete, where model output is already deleted,
    # we don't want to do the teardown process
    if hasattr(request.node, "skip_teardown"):
        return

    # If test failed, for debugging purposes, we want to keep the model output in
    # me.org
    report = request.node.stash[phase_report_key]
    if report["call"].failed:
        print("Call to test failed", request.node.nodeid)
        return

    for model_output_id in model_output_ids:
        runner.invoke(cli.model_output_delete, [model_output_id])


@pytest.fixture
def model_output_id(model_output_generator: str):
    """Generate fresh model output ID.

    Parameters
    ----------
    model_output_generator: str
        Model output generator function
    """
    return model_output_generator("base_model_output")


def test_list_endpoints(runner: CliRunner):
    """Test list-endpoints via CLI.

    Parameters
    ----------
    runner : CliRunner
        Runner object
    """
    result = runner.invoke(cli.list_endpoints)
    assert result.exit_code == 0


class TestModelOutput:
    def test_create_model_output(
        self, runner: CliRunner, model_profile_id, model_output_name
    ):
        """Test Creation of Model output."""
        result = runner.invoke(
            cli.create_new_model_output,
            [model_profile_id, model_output_name],
            standalone_mode=False,
        )

        assert result.exit_code == 0
        model_output_id = result.return_value
        assert isinstance(model_output_id, str)  # The new model output

    def test_model_output_query(self, runner: CliRunner, model_output_id: str):
        """Test Existing Model output."""
        result = runner.invoke(
            cli.model_output_query,
            [model_output_id],
        )
        assert result.exit_code == 0

    def test_model_output_update(
        self,
        runner: CliRunner,
        model_output_name: str,
        model_profile_id: str,
        model_output_id: str,
    ):
        """Test Existing Model output."""
        result = runner.invoke(
            cli.model_output_update,
            [
                model_output_id,
                # model_output_name,
                "--model-profile-id",
                model_profile_id,
                "--state-selection",
                "default",
                "--parameter-selection",
                "automated",
                "--is-bundle",
            ],
        )
        assert result.exit_code == 0

    def test_model_output_delete(
        self, request, runner: CliRunner, model_output_id: str
    ):
        request.node.skip_teardown = True
        result = runner.invoke(cli.model_output_delete, [model_output_id])
        assert result.exit_code == 0


class TestBenchmark:

    # This model_output_id will always have multiple benchmarks
    @pytest.fixture
    def model_output_id(
        self, runner: CliRunner, model_output_generator, experiment_id: str
    ):
        latest_id = None
        for i in range(2):
            latest_id = model_output_generator(f"meorg_test_benchmark{i}")
            runner.invoke(
                cli.model_output_experiments_extend,
                [latest_id, experiment_id],
            )
        return latest_id

    def _check_available_benchmarks(self, result, expected):
        available_benchmarks = result.get("benchmarks")
        assert isinstance(available_benchmarks, list)
        assert len(available_benchmarks) == expected
        return available_benchmarks

    def _check_current_benchmarks(self, result, expected):
        current_benchmarks = result.get("current")
        assert isinstance(current_benchmarks, list)
        assert len(current_benchmarks) == expected
        return current_benchmarks

    def test_model_output_benchmarks_list(
        self, runner: CliRunner, experiment_id: str, model_output_id: str
    ):
        result = runner.invoke(
            cli.model_output_benchmarks_list,
            [model_output_id, experiment_id],
            standalone_mode=False,
        )

        assert result.exit_code == 0

        self._check_available_benchmarks(result.return_value, 1)
        self._check_current_benchmarks(result.return_value, 0)

    def test_model_output_benchmarks_replace(
        self, runner: CliRunner, experiment_id: str, model_output_id: str
    ):
        result = runner.invoke(
            cli.model_output_benchmarks_list,
            [model_output_id, experiment_id],
            standalone_mode=False,
        )
        available_benchmarks = self._check_available_benchmarks(result.return_value, 1)
        self._check_current_benchmarks(result.return_value, 0)

        result = runner.invoke(
            cli.model_output_benchmarks_replace,
            [
                model_output_id,
                experiment_id,
                available_benchmarks[0]["id"],
            ],
            standalone_mode=False,
        )
        assert result.exit_code == 0

        result = runner.invoke(
            cli.model_output_benchmarks_list,
            [model_output_id, experiment_id],
            standalone_mode=False,
        )
        self._check_available_benchmarks(result.return_value, 0)
        self._check_current_benchmarks(result.return_value, 1)


def test_model_output_experiments_extend(
    runner: CliRunner, model_output_id: str, experiment_id: str
):
    result = runner.invoke(
        cli.model_output_experiments_extend,
        [model_output_id, experiment_id],
    )
    assert result.exit_code == 0


def test_model_output_experiment_delete(
    runner: CliRunner, model_output_id: str, experiment_id: str
):
    result = runner.invoke(
        cli.model_output_experiments_extend,
        [model_output_id, experiment_id],
    )
    result = runner.invoke(
        cli.model_output_experiment_delete,
        [model_output_id, experiment_id],
    )
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


def test_file_list(runner: CliRunner, model_output_id: str):
    """Test file-list via CLI.

    Parameters
    ----------
    runner : CliRunner
        Runner.
    """
    result = runner.invoke(cli.file_list, [model_output_id])
    assert result.exit_code == 0


def test_delete_file_from_output(
    runner: CliRunner, test_filepath: str, model_output_id: str
):
    """Test deleting a file from a model output.

    Parameters
    ----------
    runner : CliRunner
        Runner.
    model_output_id : str
        Model output ID.
    """

    result = runner.invoke(
        cli.file_upload, [test_filepath, test_filepath, model_output_id]
    )
    file_ids = result.output.strip()

    # Get the last file added
    file_id = file_ids.splitlines()[-1]

    # Delete it
    result = runner.invoke(cli.file_delete, [model_output_id, file_id])
    assert result.exit_code == 0


def test_delete_all_files_from_output(
    runner: CliRunner, test_filepath: str, model_output_id: str
):
    """Test deleting all files from a model output.

    Parameters
    ----------
    runner : CliRunner
        Runner.
    model_output_id : str
        Model output ID.
    """

    _ = runner.invoke(cli.file_upload, [test_filepath, test_filepath, model_output_id])

    result = runner.invoke(cli.file_delete_all, [model_output_id])
    assert result.exit_code == 0
