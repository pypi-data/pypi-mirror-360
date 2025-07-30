""" Pypeline Constants
"""

import os

# Pypeline configuration defaults
PYPELINE_YAML_PATH = os.environ.get("PYPELINE_YAML_PATH", "pypeline.yaml")
PYPELINE_CLIENT_PKG_NAME = os.environ.get("PYPELINE_CLIENT_PKG_NAME", None)
WORKER_NAME = os.environ.get("WORKER_NAME", None)
API_ACCESS_KEY = os.environ.get("API_ACCESS_KEY", None)
DEFAULT_BROKER_CALLABLE = os.environ.get(
    "DEFAULT_BROKER_CLS", "pypeline.dramatiq:configure_default_broker"
)

# Pypeline broker connections
RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://admin:password@127.0.0.1:5672")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Pypeline task defaults
PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL = int(
    os.getenv("DRAMATIQ_PARALLEL_PIPELINE_CALLBACK_BARRIER_TTL", "86400000")
)
DEFAULT_RESULT_TTL = int(os.getenv("DEFAULT_RESULT_TTL", 86400))  # seconds (1 day)
DEFAULT_TASK_TTL = int(os.getenv("DEFAULT_TASK_TTL", 600))  # seconds (10 minutes)
DEFAULT_TASK_MAX_RETRY = int(os.getenv("DEFAULT_TASK_MAX_RETRY", 3))
DEFAULT_TASK_MIN_BACKOFF = int(os.getenv("DEFAULT_TASK_MIN_BACKOFF", 15))  # seconds
DEFAULT_TASK_MAX_BACKOFF = int(
    os.getenv("DEFAULT_TASK_MAX_BACKOFF", 3600)
)  # seconds (1 hour)
DEFAULT_BROKER_CONNECTION_HEARTBEAT = int(
    os.getenv("DEFAULT_BROKER_CONNECTION_HEARTBEAT", 5)
)
DEFAULT_BROKER_CONNECTION_ATTEMPTS = int(
    os.getenv("DEFAULT_BROKER_CONNECTION_ATTEMPTS", 5)
)
DEFAULT_BROKER_BLOCKED_CONNECTION_TIMEOUT = int(
    os.getenv("DEFAULT_BROKER_BLOCKED_CONNECTION_TIMEOUT", 30)
)
DEFAULT_BROKER_HEARTBEAT_TIMEOUT = int(
    os.getenv("DEFAULT_BROKER_HEARTBEAT_TIMEOUT", 300000)
)
MESSAGE_BROKER = os.getenv("MESSAGE_BROKER", "RABBITMQ")

MS_IN_SECONDS = 1000
API_PATH_V1 = "/api/v1"

# Default 'responses' dictionary when decorating endpoints with @api.doc()
# Extend as necessary.
API_DOC_RESPONSES = {
    200: {"code": 200, "description": "Successful response."},
    400: {"code": 400, "description": "Malformed request. Verify payload is correct."},
    401: {
        "code": 401,
        "description": "Unauthorized. Verify your API Key (`accesskey`) header.",
    },
}

# Default 'params' dictionary when decorating endpoints with @api.doc()
# Extend as necessary.
API_DOC_PARAMS = {
    "accesskey": {
        "in": "header",
        "name": "accesskey",
        "description": "Your API Consumer's `accesskey`",
        "type": "string",
        "required": False,
    }
}

DEFAULT_OPENAPI_CONFIG = (
    ("SWAGGER_UI_DOC_EXPANSION", "list"),
    ("API_DOCUMENTATION_TITLE", "Pypeline API Specs"),
    ("API_DOCUMENTATION_DESCRIPTION", "Available API Endpoints"),
    ("OPENAPI_VERSION", "3.0.2"),
    ("OPENAPI_URL_PREFIX", "/api/v1"),
    ("OPENAPI_SWAGGER_APP_NAME", "Pypeline - API Reference"),
    ("OPENAPI_SWAGGER_UI_PATH", "/docs"),
    ("OPENAPI_SWAGGER_BASE_TEMPLATE", "swagger/swagger_ui.html"),
    ("OPENAPI_SWAGGER_URL", "/docs"),
    (
        "OPENAPI_SWAGGER_UI_URL",
        "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/",
    ),
    ("EXPLAIN_TEMPLATE_LOADING", False),
)
