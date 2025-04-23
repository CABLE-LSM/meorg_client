"""API Endpoints."""

# List of endpoints (specification)
ENDPOINT_LIST = "openapi.json"

# Authentication
LOGIN = "login"
LOGOUT = "logout"

# Files
FILE_LIST = "modeloutput/{id}/files"
FILE_UPLOAD = FILE_LIST
FILE_DELETE = "modeloutput/{id}/files/{fileId}"
FILE_STATUS = "files/status/{id}"

# Analysis
ANALYSIS_START = "modeloutput/{id}/start"
ANALYSIS_STATUS = "analysis/{id}/status"

# Model Outputs
MODEL_OUTPUT_CREATE = "modeloutput"
MODEL_OUTPUT_QUERY = MODEL_OUTPUT_CREATE
