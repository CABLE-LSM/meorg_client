from requests_mock import Mocker
import requests
from acme.client import Client
import pytest
from acme.utilities import load_package_data


BASE_URL = 'http://example.com'

# login
LOGIN_REQUEST = dict(email='user@example.com', password='123456')
LOGIN_REPONSE = dict(userId='user123', authToken='123456')

GET_FILE_STATUS_RESPONSE = dict()

# start_analysis
START_ANALYSIS_REQUEST = dict(model_output_id='123456')
START_ANALYSIS_RESPONSE = dict(analysisId='123456')


@pytest.fixture
def mocker():
    """Create a mocker fixture to use in all tests."""

    rm = Mocker()

    # Load the api spec
    endpoints = load_package_data('openapi.json').get('paths')

    # Loop through the endpoints
    for endpoint, config in endpoints.items():
        for method, spec in config.items():

            # The first response code appears to be the successful one
            response_code = spec.get('responses', dict()).keys[0]

            # mocked_url = f'{BASE_URL}{endpoint}

            # Create a mocked response from the response schema.
            mocked_response = dict(
                spec['responses'][response_code]['content']['application/json']
            )

            # Call the mocker and assemble
            rm.getattr(method)(

            )

    # rm.post(f'{BASE_URL}/login', json=LOGIN_REPONSE)
    # rm.post(f'{BASE_URL}/logout')
    # rm.get(f'{BASE_URL}/openapi.json')
    # rm.put(f'{BASE_URL}/modeloutput/123456/start', json=START_ANALYSIS_RESPONSE)
    return rm

@pytest.fixture
def client():
    """Create a client fixture to use in all tests."""

    return Client(base_url=BASE_URL)


def test_login(client, mocker):
    """Test login."""

    with mocker as rm:
        client.login(**LOGIN_REQUEST)

        # Ensure the headers indicating successful login are set.
        assert client.headers['X-User-Id'] == LOGIN_REPONSE['userId']
        assert client.headers['X-Auth-Token'] == LOGIN_REPONSE['authToken']


def test_logout(client, mocker):
    """Test logout."""

    with mocker as rm: 
        client.login(**LOGIN_REQUEST)
        client.logout()

        # Ensure the headers are cleared, indicating logout.
        assert client.headers == dict()


def test_start_analysis(client, mocker):
    """Test start_analysis."""

    with mocker as rm:
        response = client.start_analysis(**START_ANALYSIS_REQUEST)
        assert response.json() == START_ANALYSIS_RESPONSE


def test_list_endpoints(client, mocker):
    """Test list_endpoints."""

    with mocker as rm:
        endpoints = client.list_endpoints()
        # Just ensure a response is returned for now
        # We can make this more comprehensive later
        assert isinstance(endpoints, requests.Response)