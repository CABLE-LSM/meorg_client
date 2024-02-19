"""Custom exceptions."""


class RequestException(Exception):
    """Raised when a request fails.

    Parameters
    ----------
    status_code : int
        HTTP status code.
    response_text : str
        Response text.
    """

    def __init__(self, status_code, response_text):
        self.status_code = status_code
        self.response_text = response_text
        msg = f"Request failed with status code {status_code}: {response_text}"
        super().__init__(msg)
