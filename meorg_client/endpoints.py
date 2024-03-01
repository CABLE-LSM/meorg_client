"""API Endpoints."""

# List of endpoints (specification)
ENDPOINT_LIST = "openapi.json"

# Authentication
LOGIN = "login"
LOGOUT = "logout"

# Files
FILE_LIST = "modeloutput/{id}/files"
FILE_UPLOAD = "files"
FILE_STATUS = "files/status/{id}"

# Analysis
ANALYSIS_START = "modeloutput/{id}/start"
ANALYSIS_STATUS = "modeloutput/{id}/status"
