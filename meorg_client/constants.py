"""Constants."""

# Valid HTTP methods
HTTP_POST = "POST"
HTTP_PUT = "PUT"
HTTP_GET = "GET"
HTTP_DELETE = "DELETE"
HTTP_PUT = "PUT"
VALID_METHODS = [HTTP_PUT, HTTP_GET, HTTP_DELETE, HTTP_PUT, HTTP_POST]

# Methods that interpolate parameters into the URL
INTERPOLATING_METHODS = [HTTP_GET, HTTP_PUT]

# RFC 2616 states status in the 2xx range are considered successful
HTTP_STATUS_SUCCESS_RANGE = range(200, 300)

# Content types
HTTP_CONTENT_TYPE_JSON = "application/json"

# Production URL
MEORG_URL = "https://modelevaluation.org"
