from requests_mock import Mocker
import requests
from meorg_client.client import Client
import pytest
from meorg_client.utilities import load_package_data, get_installed_data_root
import meorg_client.constants as mcc
import meorg_client.endpoints as endpoints
from urllib.parse import urljoin

# For convenience
BASE_URL = "http://example.com"
STR_EXAMPLE = "abcdefg"

# Canned requests
REQUEST_EXAMPLES = {
    endpoints.LOGIN: dict(email="user@example.com", password="123456"),
    endpoints.LOGOUT: dict(),
    endpoints.FILE_UPLOAD: b"binary",
    endpoints.FILE_STATUS: dict(id=STR_EXAMPLE),
    endpoints.FILE_LIST: dict(id=STR_EXAMPLE),
    endpoints.ANALYSIS_START: dict(id=STR_EXAMPLE),
    endpoints.ANALYSIS_STATUS: dict(id=STR_EXAMPLE),
}

# Canned responses
RESPONSE_EXAMPLES = {
    endpoints.LOGIN: dict(userId="user123", authToken="123456"),
    endpoints.LOGOUT: dict(),
    endpoints.FILE_UPLOAD: dict(status="success", data=dict(jobId=STR_EXAMPLE)),
    endpoints.FILE_STATUS: dict(
        status="success",
        data=dict(
            status="complete", files=[dict(fileId="123456", filename=STR_EXAMPLE)]
        ),
    ),
    endpoints.FILE_LIST: dict(status="success", data=[STR_EXAMPLE]),
    endpoints.ANALYSIS_START: dict(status="success", data=dict(analysisId=STR_EXAMPLE)),
    endpoints.ANALYSIS_STATUS: dict(
        status="success",
        data=dict(status=STR_EXAMPLE, url=STR_EXAMPLE, files=[STR_EXAMPLE]),
    ),
}


@pytest.fixture
def mocker():
    """Create a mocker fixture to use in all tests."""

    rm = Mocker()

    # Load the api spec
    api_spec = load_package_data("openapi.json")

    # Loop through the endpoints
    for url, methods in api_spec["paths"].items():
        for method, spec in methods.items():
            # Remove the leading slash from the url from the spec.
            url = url.lstrip("/")

            # Assemble the mock url
            mocked_url = urljoin(BASE_URL, url)

            # Add id if it is a get or put method
            if method.upper() in mcc.INTERPOLATING_METHODS:
                mocked_url = mocked_url.format(id=STR_EXAMPLE)

            # Add it to the mocker
            rm.__getattribute__(method)(mocked_url, json=RESPONSE_EXAMPLES[url])

    return rm


@pytest.fixture
def client():
    """Create a client fixture to use in all tests."""

    return Client(base_url=BASE_URL)


def test_login(client, mocker):
    """Test login."""

    request = REQUEST_EXAMPLES[endpoints.LOGIN]
    response = RESPONSE_EXAMPLES[endpoints.LOGIN]

    with mocker as rm:
        client.login(**request)

        # Ensure the headers indicating successful login are set.
        assert client.headers["X-User-Id"] == response["userId"]
        assert client.headers["X-Auth-Token"] == response["authToken"]


def test_logout(client, mocker):
    """Test logout."""

    request = REQUEST_EXAMPLES[endpoints.LOGIN]

    with mocker as rm:
        client.login(**request)
        client.logout()

        # Ensure the headers are cleared, indicating logout.
        assert client.headers == dict()
        assert client.last_response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_upload(client, mocker):
    """Test upload."""

    # Just use the api spec as the file to upload, it doesn't matter for testing.
    filepath = get_installed_data_root() / "openapi.json"

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[endpoints.LOGIN])
        response = client.upload_file(filepath)
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_get_file_status(client, mocker):
    """Test get_file_status."""

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[endpoints.LOGIN])
        response = client.get_file_status(**REQUEST_EXAMPLES[endpoints.FILE_STATUS])
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_list_files(client, mocker):
    """Test list_files."""

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[endpoints.LOGIN])
        response = client.list_files(**REQUEST_EXAMPLES[endpoints.FILE_LIST])
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_start_analysis(client, mocker):
    """Test start_analysis."""

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[endpoints.LOGIN])
        response = client.start_analysis(**REQUEST_EXAMPLES[endpoints.ANALYSIS_START])
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_get_analysis_status(client, mocker):
    """Test get_analysis_status."""

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[endpoints.LOGIN])
        response = client.get_analysis_status(
            **REQUEST_EXAMPLES[endpoints.ANALYSIS_STATUS]
        )
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE
