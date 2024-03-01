"""Client object."""
import requests
import hashlib as hl
import json
import os
from typing import Union
from urllib.parse import urljoin
from meorg_client.exceptions import RequestException
import meorg_client.constants as mcc
import meorg_client.endpoints as endpoints


class Client:
    def __init__(self, base_url=mcc.MEORG_URL, email=None, password=None):
        """ME.org Client object.

        Suppying email and password will automatically log in.

        Parameters
        ----------
        base_url : str
            Base URL to API.
        email : str, optional
            Registered email address, by default None
        password : str, optional
            User password, by default None
        """
        self.base_url = base_url
        self.headers = dict()
        self.last_response = None

        # Automatically login.
        if email is not None and password is not None:
            self.login(email, password)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict = None,
        headers: dict = None,
        return_json=True,
    ) -> Union[dict, requests.Response]:
        """Make the request

        Parameters
        ----------
        method : str
            Method name (GET, POST, PUT, UPDATE, DELETE)
        endpoint : str
            URL slug to add to the base url.
        data : dict, optional
            Key/value pairs of data to send., by default None
        headers : dict, optional
            Headers to add to the request, by default None
        return_json : bool, optional,
            Automatically decode JSON response data, default True


        Returns
        -------
        dict or requests.Response
            Decoded JSON response, or raw response.

        Raises
        ------
        Exception
            Raised when there is an issue.
        """

        # Cast to uppercase, for consisency
        method = method.upper()

        if method not in mcc.VALID_METHODS:
            raise Exception(f"Invalid method {method}")

        # GET/PUT requests have the data interpolated into the url
        if method in mcc.INTERPOLATING_METHODS:
            endpoint = endpoint.format(**data)

        url = urljoin(self.base_url, endpoint)
        all_headers = {**self.headers, **headers} if headers else self.headers

        # Update the client with the last response
        self.last_response = requests.request(
            method, url, data=data, headers=all_headers
        )

        # RFC 2616 states status in the 2xx range are considered successful
        if self.last_response.status_code in mcc.HTTP_STATUS_SUCCESS_RANGE:
            # Return JSON if that's what it is (this should be the default)
            if (
                self.last_response.headers.get("Content-Type", str)
                == mcc.HTTP_CONTENT_TYPE_JSON
                and return_json == True
            ):
                return self.last_response.json()

            return self.last_response

        else:
            raise RequestException(
                self.last_response.status_code, self.last_response.text
            )

    def login(self, email: str, password: str):
        """Log the user into ME.org.

        Parameters
        ----------
        email : str
            Registered email address.
        password : str
            Password (will be hashed)

        Raises
        ------
        Exception
            When the login fails.
        """

        # Assemble payload
        login_data = {
            "email": email,
            "password": hl.sha256(password.encode("UTF-8")).hexdigest(),
            "hashed": "true",
        }

        # Call
        response = self._make_request("post", endpoint=endpoints.LOGIN, data=login_data)

        # Successful login
        if response.status_code == 200:
            auth_headers = {
                "X-User-Id": response.json()["userId"],
                "X-Auth-Token": response.json()["authToken"],
            }

            self.headers.update(auth_headers)

        # Unsuccessful login (technically this will have already failed)
        else:
            raise Exception("Login failed")

    def logout(self):
        """Log the user out. Likely not necessary, can just let sessions expire.

        Returns
        -------
        dict or requests.Response
            Response from ME.org.
        """
        response = self._make_request(mcc.HTTP_POST, endpoint=endpoints.LOGOUT)

        # Clear the headers.
        self.headers = dict()

        return response

    def get_file_status(self, id: str) -> Union[dict, requests.Response]:
        """Get the file status.

        Parameters
        ----------
        id : str
            ID of the file.

        Returns
        -------
        dict or requests.Response
            Response from ME.org.
        """
        return self._make_request(
            method=mcc.HTTP_GET, endpoint=endpoints.FILE_STATUS, data=dict(id=id)
        )

    def upload_file(self, file_path: str) -> Union[dict, requests.Response]:
        """Upload a file.

        Parameters
        ----------
        file_path : str
            Path to the file.

        Returns
        -------
        Union[dict, requests.Response]
            Response from ME.org.
        """
        return self._make_request(
            method=mcc.HTTP_POST,
            endpoint=endpoints.FILE_UPLOAD,
            data=open(file_path, "rb").read(),
        )

    def list_files(self, id: str) -> Union[dict, requests.Response]:
        """Get a list of model outputs.

        Parameters
        ----------
        id : str
            Model output ID

        Returns
        -------
        dict or requests.Response
            Response from ME.org.
        """
        return self._make_request(
            method=mcc.HTTP_GET, endpoint=endpoints.FILE_LIST, data=dict(id=id)
        )

    def start_analysis(self, id: str) -> Union[dict, requests.Response]:
        """Start the analysis chain.

        Parameters
        ----------
        id : str
            Model output ID.

        Returns
        -------
        dict or requests.Response
            Response from ME.org.
        """
        return self._make_request(
            method=mcc.HTTP_PUT, endpoint=endpoints.ANALYSIS_START, data=dict(id=id)
        )

    def get_analysis_status(self, id: str) -> Union[dict, requests.Response]:
        """Check the status of the analysis chain.

        Parameters
        ----------
        id : str
            Analysis ID.

        Returns
        -------
        dict or requests.Response
            Response from ME.org.
        """
        return self._make_request(
            method=mcc.HTTP_GET, endpoint=endpoints.ANALYSIS_STATUS, data=dict(id=id)
        )

    def list_endpoints(self) -> Union[dict, requests.Response]:
        """List the endpoints available to the user.

        Paths are available at .get('paths').keys()

        Returns
        -------
        dict or requests.Response
            Response from ME.org.
        """

        return self._make_request(method=mcc.HTTP_GET, endpoint=endpoints.ENDPOINT_LIST)
