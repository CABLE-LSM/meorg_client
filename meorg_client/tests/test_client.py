"""A test suite to work against the dev instance at NCI."""
import os
import pytest
from meorg_client.client import Client
import meorg_client.utilities as mu
from conftest import store


def _get_authenticated_client():
    email = os.environ.get("MEORG_EMAIL")
    password = os.environ.get("MEORG_PASSWORD")
    model_output_id = os.environ.get("MEORG_MODEL_OUTPUT_ID")

    client = Client(email=email, password=password)

    if None in [email, password, model_output_id, client.base_url]:
        raise TypeError("Test Secrets not set!!!")

    # Attach the model output id for convenience in testing
    client._model_output_id = model_output_id

    return client


@pytest.fixture
def client():
    return _get_authenticated_client()


def test_login():
    """Test login."""
    _client = _get_authenticated_client()
    assert "X-Auth-Token" in _client.headers.keys()


def test_list_endpoints(client):
    """Test list_endpoints."""
    response = client.list_endpoints()
    assert client.success()
    assert isinstance(response, dict)


def test_upload_file(client):
    """Test the uploading of a file."""
    # Upload the file.
    filepath = os.path.join(mu.get_installed_data_root(), "test/test.txt")

    # Upload the file
    response = client.upload_file(filepath)

    # Make sure it worked
    assert client.success()

    # Store the response.
    store.set("file_upload", response)


def test_file_status(client):
    # Get the response
    job_id = store.get("file_upload").get("data").get("jobId")

    response = client.get_file_status(job_id)
    assert client.success()

    store.set("file_status", response)


def test_file_list(client):
    response = client.list_files(client._model_output_id)
    assert client.success()
    assert isinstance(response.get("data").get("files"), list)


def test_attach_files_to_model_output(client):
    # Get the file id from the job id
    file_id = store.get("file_status").get("data").get("files")[0].get("file")

    # Attach it to the model output
    _ = client.attach_files_to_model_output(client._model_output_id, [file_id])

    assert client.success()


def test_start_analysis(client):
    response = client.start_analysis(client._model_output_id)
    assert client.success()
    store.set("start_analysis", response)


def test_get_analysis_status(client):
    # Get the analysis id from the store
    analysis_id = store.get("start_analysis").get("data").get("analysisId")
    _ = client.get_analysis_status(analysis_id)
    assert client.success()


def test_logout(client):
    """Test logout."""
    client.logout()
    assert "X-Auth-Token" not in client.headers.keys()
