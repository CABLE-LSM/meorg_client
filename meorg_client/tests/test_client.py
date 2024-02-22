from requests_mock import Mocker
import requests
from meorg_client.client import Client
import pytest
from meorg_client.utilities import load_package_data, get_installed_data_root
import meorg_client.constants as mcc
from urllib.parse import urljoin


BASE_URL = "http://example.com"
STR_EXAMPLE = "abcdefg"

REQUEST_EXAMPLES = {
    mcc.ENDPOINTS["login"]: dict(email="user@example.com", password="123456"),
    mcc.ENDPOINTS["logout"]: dict(),
    mcc.ENDPOINTS["file_upload"]: b"binary",
    mcc.ENDPOINTS["file_status"]: dict(id=STR_EXAMPLE),
    mcc.ENDPOINTS["file_list"]: dict(id=STR_EXAMPLE),
    mcc.ENDPOINTS["analysis_start"]: dict(id=STR_EXAMPLE),
    mcc.ENDPOINTS["analysis_status"]: dict(id=STR_EXAMPLE),
}

RESPONSE_EXAMPLES = {
    mcc.ENDPOINTS["login"]: dict(userId="user123", authToken="123456"),
    mcc.ENDPOINTS["logout"]: dict(),
    mcc.ENDPOINTS["file_upload"]: dict(status="success", data=dict(jobId=STR_EXAMPLE)),
    mcc.ENDPOINTS["file_status"]: dict(
        status="success",
        data=dict(
            status="complete", files=[dict(fileId="123456", filename=STR_EXAMPLE)]
        ),
    ),
    mcc.ENDPOINTS["file_list"]: dict(status="success", data=[STR_EXAMPLE]),
    mcc.ENDPOINTS["analysis_start"]: dict(
        status="success", data=dict(analysisId=STR_EXAMPLE)
    ),
    mcc.ENDPOINTS["analysis_status"]: dict(
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

    request = REQUEST_EXAMPLES[mcc.ENDPOINTS["login"]]
    response = RESPONSE_EXAMPLES[mcc.ENDPOINTS["login"]]

    with mocker as rm:
        client.login(**request)

        # Ensure the headers indicating successful login are set.
        assert client.headers["X-User-Id"] == response["userId"]
        assert client.headers["X-Auth-Token"] == response["authToken"]


def test_logout(client, mocker):
    """Test logout."""

    request = REQUEST_EXAMPLES[mcc.ENDPOINTS["login"]]

    with mocker as rm:
        client.login(**request)
        client.logout()

        # Ensure the headers are cleared, indicating logout.
        assert client.headers == dict()
        assert client.last_response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_upload(client, mocker):
    """Test upload."""

    # Just use the api spec as the file to upload, it doesn't matter
    filepath = get_installed_data_root() / "openapi.json"

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[mcc.ENDPOINTS["login"]])
        response = client.upload_file(filepath)
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_get_file_status(client, mocker):
    """Test get_file_status."""

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[mcc.ENDPOINTS["login"]])
        response = client.get_file_status(
            **REQUEST_EXAMPLES[mcc.ENDPOINTS["file_status"]]
        )
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_list_files(client, mocker):
    """Test list_files."""

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[mcc.ENDPOINTS["login"]])
        response = client.list_files(**REQUEST_EXAMPLES[mcc.ENDPOINTS["file_list"]])
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_start_analysis(client, mocker):
    """Test start_analysis."""

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[mcc.ENDPOINTS["login"]])
        response = client.start_analysis(
            **REQUEST_EXAMPLES[mcc.ENDPOINTS["analysis_start"]]
        )
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE


def test_get_analysis_status(client, mocker):
    """Test get_analysis_status."""

    with mocker as rm:
        client.login(**REQUEST_EXAMPLES[mcc.ENDPOINTS["login"]])
        response = client.get_analysis_status(
            **REQUEST_EXAMPLES[mcc.ENDPOINTS["analysis_status"]]
        )
        assert response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE
