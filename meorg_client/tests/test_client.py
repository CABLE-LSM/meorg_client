"""A test suite to work against the dev instance at NCI."""

import os
import pytest
from meorg_client.client import Client
import meorg_client.utilities as mu
import tempfile as tf
from conftest import phase_report_key


def _get_authenticated_client() -> Client:
    """Get an authenticated client for tests.

    Returns
    -------
    meorg_client.client.Client
        Client object.

    Raises
    ------
    TypeError
        Raised with test secrets are not set in the environment.
    """

    # Get the details from the environment.
    email = os.environ.get("MEORG_EMAIL")
    password = os.environ.get("MEORG_PASSWORD")

    # Connect
    client = Client(email=email, password=password)

    # Ensure everything is set
    if None in [email, password, client.base_url]:
        raise TypeError("Test Secrets not set!!!")

    return client


@pytest.fixture(scope="module")
def client() -> Client:
    """Get an authenticated client.

    Returns
    -------
    Client
        Authenticated client.
    """
    return _get_authenticated_client()


@pytest.fixture
def test_filepath() -> str:
    """Get a test filepath from the installation.

    Returns
    -------
    str
        Path to the test filepath.
    """
    return os.path.join(mu.get_installed_data_root(), "test/test.txt")


def test_login():
    """Test login."""
    # Get a client, note we are calling this direct to test the login explicitly
    _client = _get_authenticated_client()
    assert "X-Auth-Token" in _client.headers.keys()


def test_list_endpoints(client: Client):
    """Test list_endpoints.

    Parameters
    ----------
    client : Client
        Client.
    """
    response = client.list_endpoints()
    assert client.success()
    assert isinstance(response, dict)


@pytest.fixture
def model_output_generator(request, client: Client, model_profile_id: str):
    """A generator function for creating new model outputs before running a test.

       After the test has run, automatically deletes all model outputs created within
       the test

    Parameters
    -------
    request:
        Request object by pytest

    client : Client
        Client.

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
        response = client.model_output_create(model_profile_id, model_output_name)
        model_output_id = response.get("data").get("modeloutput")
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
        client.model_output_delete(model_output_id)


@pytest.fixture
def model_output_id(model_output_generator: str):
    """Generate fresh model output ID.

    Parameters
    ----------
    model_output_generator: str
        Model output generator function
    """
    return model_output_generator("base_model_output")


class TestModelOutput:

    def test_create_model_output(
        self, client: Client, model_profile_id: str, model_output_name: str
    ):
        """Test Creation of Model output."""
        response = client.model_output_create(model_profile_id, model_output_name)
        assert client.success()

        model_output_id = response.get("data").get("modeloutput")
        assert model_output_id is not None

        self.test_model_output_query(client, model_output_id)

    def test_model_output_query(self, client: Client, model_output_id: str):
        """Test Existing Model output."""
        response = client.model_output_query(model_output_id)
        assert client.success()

        response_model_output_data = response.get("data").get("modeloutput")
        assert response_model_output_data.get("id") == model_output_id

    def test_model_output_update(
        self,
        client: Client,
        model_output_id: str,
        model_profile_id: str,
    ):
        """Test updation of model output."""

        update_data = {
            "name": "updated_mo_name",
            "model": model_profile_id,
            "state_selection": "default model initialisation",
            "parameter_selection": "automated calibration",
            "comments": "updated model output pytest",
            "is_bundle": False,
        }
        _ = client.model_output_update(model_output_id, update_data)
        assert client.success()

    def test_model_output_delete(self, request, client: Client, model_output_id: str):
        request.node.skip_teardown = True
        _ = client.model_output_delete(model_output_id)
        assert client.success()


class TestBenchmark:

    # This model_output_id will always have multiple benchmarks
    @pytest.fixture
    def model_output_id(
        self, client: Client, model_output_generator, experiment_id: str
    ):
        latest_id = None
        for i in range(2):
            latest_id = model_output_generator(f"meorg_test_benchmark{i}")
            client.model_output_experiments_extend(latest_id, [experiment_id])
        return latest_id

    def _check_available_benchmarks(self, response, expected):
        available_benchmarks = response.get("data").get("benchmarks")
        assert isinstance(available_benchmarks, list)
        assert len(available_benchmarks) == expected
        return available_benchmarks

    def _check_current_benchmarks(self, response, expected):
        current_benchmarks = response.get("data").get("current")
        assert isinstance(current_benchmarks, list)
        assert len(current_benchmarks) == expected
        return current_benchmarks

    def test_model_output_benchmarks_list(
        self, client: Client, model_output_id: str, experiment_id: str
    ):

        response = client.model_output_benchmarks_list(model_output_id, experiment_id)
        self._check_available_benchmarks(response, 1)
        self._check_current_benchmarks(response, 0)
        assert client.success()

    def test_model_output_benchmarks_replace(
        self, client: Client, model_output_id: str, experiment_id: str
    ):
        response = client.model_output_benchmarks_list(model_output_id, experiment_id)
        available_benchmarks = self._check_available_benchmarks(response, 1)
        self._check_current_benchmarks(response, 0)

        client.model_output_benchmarks_replace(
            model_output_id,
            experiment_id,
            [available_benchmarks[0]["id"]],
        )
        assert client.success()

        response = client.model_output_benchmarks_list(model_output_id, experiment_id)
        self._check_available_benchmarks(response, 0)
        self._check_current_benchmarks(response, 1)


def test_model_output_experiments_extend(
    client: Client, model_output_id: str, experiment_id: str
):
    client.model_output_experiments_extend(model_output_id, [experiment_id])
    assert client.success()


def test_model_output_experiment_delete(
    client: Client, model_output_id: str, experiment_id: str
):
    # For now, since fresh model output id
    client.model_output_experiments_extend(model_output_id, [experiment_id])
    client.model_output_experiment_delete(model_output_id, experiment_id)
    assert client.success()


def test_upload_file(client: Client, test_filepath: str, model_output_id: str):
    """Test the uploading of a file.

    Parameters
    ----------
    client : Client
        _description_
    test_filepath : str
        _description_
    model_output_id : str
        _description_
    """
    # Upload the file
    response = client.upload_files(test_filepath, id=model_output_id)[0]

    # Make sure it worked
    assert client.success()


def test_upload_file_multiple(client: Client, test_filepath: str, model_output_id: str):
    """Test the uploading of multiple files in sequence.

    Parameters
    ----------
    client : Client
        Client.
    test_filepath : str
        Test filepath.
    model_output_id : str
        Model output ID.
    """
    # Upload the files
    responses = client.upload_files([test_filepath, test_filepath], model_output_id)

    # Make sure they all worked
    assert all(
        [response.get("data").get("files")[0].get("id") for response in responses]
    )


def test_file_list(client: Client, model_output_id: str):
    """Test the listing of files for a model output.

    Parameters
    ----------
    client : Client
        Client.
    model_output_id : str
        Model output ID.
    """
    response = client.list_files(model_output_id)
    assert client.success()
    assert isinstance(response.get("data").get("files"), list)


class TestAnalysis:

    @pytest.fixture
    def model_output_id_analysis(
        self,
        client: Client,
        test_filepath: str,
        experiment_id: str,
        model_output_generator,
    ):
        model_output_id = model_output_generator("meorg_test_analysis")
        client.model_output_experiments_extend(model_output_id, [experiment_id])
        client.upload_files([test_filepath, test_filepath], model_output_id)
        return model_output_id

    @pytest.fixture
    def analysis_id(
        self, client: Client, model_output_id_analysis: str, experiment_id: str
    ):
        response = client.start_analysis(model_output_id_analysis, experiment_id)
        return response.get("data").get("analysisId")

    def test_start_analysis(
        self, client: Client, model_output_id_analysis: str, experiment_id: str
    ):
        """Test starting an analysis.

        Parameters
        ----------
        client : Client
            Client.
        model_output_id : str
            Model output ID.
        """
        _ = client.start_analysis(model_output_id_analysis, experiment_id)
        assert client.success()

    def test_get_analysis_status(self, client: Client, analysis_id: str):
        """Test getting the analysis status.

        Parameters
        ----------
        client : Client
            Client.
        """
        _ = client.get_analysis_status(analysis_id)
        assert client.success()


@pytest.mark.xfail(strict=False)
def test_upload_file_large(client: Client, model_output_id: str):
    """Test the uploading of a large-ish file.

    Parameters
    ----------
    client : Client
        Client.
    model_output_id : str
        Model output ID.
    """

    # Create an in-memory 10mb file
    size = 10000000
    data = bytearray(os.urandom(size))

    with tf.NamedTemporaryFile() as tmp:
        # Write and set cursor
        tmp.write(data)
        tmp.seek(0)

        # tmp files have no extension, so we have to rename them
        new_name = tmp.name + ".nc"
        os.rename(tmp.name, new_name)
        tmp.name = new_name

        # Upload and ensure it worked
        _ = client.upload_files(new_name, model_output_id)

    assert client.success()


def test_upload_file_parallel(client: Client, test_filepath: str, model_output_id: str):
    """Test the uploading of multiple files in parallel.

    Parameters
    ----------
    client : Client
        Client.
    test_filepath : str
        Test filepath.
    model_output_id : str
        Model output ID.
    """
    # Upload the file
    responses = client.upload_files(
        [test_filepath, test_filepath], id=model_output_id, n=2, progress=True
    )

    # Make sure they all worked
    assert all(
        [response.get("data").get("files")[0].get("id") for response in responses]
    )


def test_upload_file_parallel_no_progress(
    client: Client, test_filepath: str, model_output_id: str
):
    """Test parallel uploads, but switch off the progress bar.

    Parameters
    ----------
    client : Client
        Client.
    test_filepath : str
        Test filepath.
    model_output_id : str
        Model output ID.
    """
    # Upload the file
    responses = client.upload_files(
        [test_filepath, test_filepath], id=model_output_id, n=2, progress=False
    )

    # Make sure it worked
    assert all(
        [response.get("data").get("files")[0].get("id") for response in responses]
    )


def test_delete_file_from_model_output(
    client: Client, test_filepath: str, model_output_id: str
):
    """Test deleting a file from a model output.

    Parameters
    ----------
    client : Client
        Client.
    model_output_id : str
        Model output ID.
    """
    file_upload = client.upload_files(test_filepath, id=model_output_id)[0]

    # Retrieve the uploaded file ID from earlier.
    file_id = file_upload.get("data").get("files")[0].get("id")

    # Retieve the file list from earlier.
    files = client.list_files(model_output_id)

    # Convert to a list of JUST the IDs, none of the extra attributes.
    file_ids = [f.get("id") for f in files.get("data").get("files")]

    # Check that it is in there to begin with... should be.
    assert file_id in file_ids

    # Delete that one file.
    client.delete_file_from_model_output(file_id=file_id, id=model_output_id)

    # Get a fresh list from the server
    files = client.list_files(model_output_id)

    # Unpack again
    file_ids = [f.get("id") for f in files.get("data").get("files")]

    # Make sure it has been removed
    assert file_id not in file_ids


def test_delete_all_files_from_model_output(
    client: Client, test_filepath: str, model_output_id: str
):
    """Test deleting all files from a model output.

    Parameters
    ----------
    client : Client
        Client.
    model_output_id : str
        Model output ID.
    """

    # Upload a list of files
    client.upload_files([test_filepath, test_filepath], model_output_id)

    # Get the list of files and unpack to list
    files = client.list_files(model_output_id)
    file_ids = [f.get("id") for f in files.get("data").get("files")]

    # Make sure the list is more than 2 items long.
    assert len(file_ids) >= 2

    # Delete everything
    client.delete_all_files_from_model_output(model_output_id)

    # Get a fresh list from the server, unpack
    files = client.list_files(model_output_id)
    file_ids = [f.get("id") for f in files.get("data").get("files")]

    # Ensure the list is empty
    assert len(file_ids) == 0


def test_logout(client: Client):
    """Test logout.

    Parameters
    ----------
    client : Client
        Client
    """
    # Log out
    client.logout()

    # Ensure the token is cleared
    assert "X-Auth-Token" not in client.headers.keys()
