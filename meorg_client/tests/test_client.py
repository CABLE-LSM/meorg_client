"""A test suite to work against the dev instance at NCI."""

import os
import pytest
from meorg_client.client import Client
import meorg_client.utilities as mu
from conftest import store
import tempfile as tf


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
    model_output_id = os.environ.get("MEORG_MODEL_OUTPUT_ID")

    # Connect
    client = Client(email=email, password=password)

    # Ensure everything is set
    if None in [email, password, model_output_id, client.base_url]:
        raise TypeError("Test Secrets not set!!!")

    # Attach the model output id for convenience in testing
    client._model_output_id = model_output_id

    return client


def _get_test_file():
    return os.path.join(mu.get_installed_data_root(), "test/test.txt")


@pytest.fixture
def client() -> Client:
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
    _client = _get_authenticated_client()
    assert "X-Auth-Token" in _client.headers.keys()


def test_list_endpoints(client: Client):
    """Test list_endpoints."""
    response = client.list_endpoints()
    assert client.success()
    assert isinstance(response, dict)


def test_upload_file(client: Client, test_filepath: str):
    """Test the uploading of a file."""
    # Upload the file
    response = client.upload_files(test_filepath)

    # Make sure it worked
    assert client.success()

    # Store the response.
    store.set("file_upload", response)


def test_upload_file_multiple(client: Client, test_filepath: str):
    """Test the uploading of a file."""

    # Upload the file
    response = client.upload_files([test_filepath, test_filepath])

    # Make sure it worked
    assert client.success()

    # Store the response.
    store.set("file_upload_multiple", response)


def test_file_list(client: Client):
    """Test the listinf of files for a model output."""
    response = client.list_files(client._model_output_id)
    assert client.success()
    assert isinstance(response.get("data").get("files"), list)


def test_attach_files_to_model_output(client: Client):
    # Get the file id from the job id
    file_id = store.get("file_upload").get("data").get("files")[0].get("file")

    # Attach it to the model output
    _ = client.attach_files_to_model_output(client._model_output_id, [file_id])

    assert client.success()


def test_start_analysis(client: Client):
    """Test starting an analysis."""
    response = client.start_analysis(client._model_output_id)
    assert client.success()
    store.set("start_analysis", response)


def test_get_analysis_status(client: Client):
    """Test getting the analysis status."""
    # Get the analysis id from the store
    analysis_id = store.get("start_analysis").get("data").get("analysisId")
    _ = client.get_analysis_status(analysis_id)
    assert client.success()


@pytest.mark.xfail(strict=False)
def test_upload_file_large(client: Client):
    """Test the uploading of a large-ish file."""

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
        _ = client.upload_files(new_name)

    assert client.success()


def test_upload_files_with_attach(client: Client):
    """Test that the upload can also attach in the same method call."""
    filepath = _get_test_file()
    _ = client.upload_files([filepath, filepath], attach_to=client._model_output_id)
    assert client.success()


def test_upload_file_parallel(client: Client, test_filepath: str):
    """Test the uploading of a file."""
    # Upload the file
    responses = client.upload_files_parallel([test_filepath, test_filepath], n=2)

    # Make sure it worked
    assert all(
        [response.get("data").get("files")[0].get("file") for response in responses]
    )


def test_upload_file_parallel_with_attach(client: Client, test_filepath: str):
    """Test the uploading of a file with a model output ID to attach."""
    # Upload the file
    responses = client.upload_files_parallel(
        [test_filepath, test_filepath], n=2, attach_to=client._model_output_id
    )

    # Make sure it worked
    assert all(
        [response.get("data").get("files")[0].get("file") for response in responses]
    )


def test_detach_all_files_from_model_output(client: Client):
    """Test detaching all files from a model output."""

    # Remove them all
    _ = client.detach_all_files_from_model_output(client._model_output_id)
    detached_files = client.list_files(client._model_output_id)

    assert client.last_response.ok
    assert len(detached_files.get("data").get("files")) == 0


def test_logout(client: Client):
    """Test logout."""
    client.logout()
    assert "X-Auth-Token" not in client.headers.keys()
