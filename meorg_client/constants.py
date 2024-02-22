"""Constants."""

# Valid HTTP methods
VALID_METHODS = ["POST", "GET", "DELETE", "PUT"]

# Methods that interpolate parameters into the URL
INTERPOLATING_METHODS = ["GET", "PUT"]

# RFC 2616 states status in the 2xx range are considered successful
HTTP_STATUS_SUCCESS_RANGE = range(200, 300)

HTTP_CONTENT_TYPES = dict(json="application/json")

# Production URL
MEORG_URL = "https://modelevaluation.org"

# API Endpoints
ENDPOINTS = dict(
    analysis_start="modeloutput/{id}/start",
    analysis_status="modeloutput/{id}/status",
    endpoints_list="openapi.json",
    login="login",
    logout="logout",
    file_list="modeloutput/{id}/files",
    file_status="files/status/{id}",
    file_upload="files",
)
