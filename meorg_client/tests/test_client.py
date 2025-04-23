"""A test suite to work against the dev instance at NCI."""

import os
import pytest
from meorg_client.client import Client
import meorg_client.utilities as mu
from conftest import store
import tempfile as tf
import time


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


@pytest.fixture
def model_output_id() -> str:
    """Get the model output ID.

    Returns
    -------
    str
        Model output ID.
    """
    return os.environ.get("MEORG_MODEL_OUTPUT_ID")


@pytest.fixture
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


def test_create_model_output(
    client: Client, model_profile_id: str, experiment_id: str, model_output_name: str
):
    """Test Creation of Model output."""
    response = client.model_output_create(
        model_profile_id, experiment_id, model_output_name
    )
    assert client.success()

    model_output_id = response.get("data").get("modeloutput")
    assert model_output_id is not None

    test_model_output_query(client, model_output_id)


def test_model_output_query(client: Client, model_output_id: str):
    """Test Existing Model output."""
    response = client.model_output_query(model_output_id)
    assert client.success()

    response_model_output_data = response.get("data").get("modeloutput")
    assert response_model_output_data.get("id") == model_output_id


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

    # Store the response.
    store.set("file_upload", response)


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

    # Store the response.
    store.set("file_upload_multiple", responses)


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
    store.set("file_list", response)


def test_start_analysis(client: Client, model_output_id: str):
    """Test starting an analysis.

    Parameters
    ----------
    client : Client
        Client.
    model_output_id : str
        Model output ID.
    """
    # Wait 5s for data to move from cache to store (otherwise analysis will fail, still might)
    time.sleep(5)
    response = client.start_analysis(model_output_id)
    assert client.success()

    # Store result for status check below
    store.set("start_analysis", response)


def test_get_analysis_status(client: Client):
    """Test getting the analysis status.

    Parameters
    ----------
    client : Client
        Client.
    """
    # Get the analysis id from the store
    analysis_id = store.get("start_analysis").get("data").get("analysisId")
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


def test_delete_file_from_model_output(client: Client, model_output_id: str):
    """Test deleting a file from a model output.

    Parameters
    ----------
    client : Client
        Client.
    model_output_id : str
        Model output ID.
    """

    # Retrieve the uploaded file ID from earlier.
    file_id = store.get("file_upload").get("data").get("files")[0].get("id")

    # Retieve the file list from earlier.
    files = store.get("file_list")

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


def test_delete_all_files_from_model_output(client: Client, model_output_id: str):
    """Test deleting all files from a model output.

    Parameters
    ----------
    client : Client
        Client.
    model_output_id : str
        Model output ID.
    """

    # Get the list of files and unpack to list
    files = store.get("file_list")
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
