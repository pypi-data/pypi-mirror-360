""" Flask specific decorators (primarily for auth activities and app context)
"""
import os
import logging
from http import HTTPStatus
from functools import wraps
from flask import request
from flask import abort

logger = logging.getLogger(__name__)


def require_accesskey(fn):
    """Convenience decorator to add to a web route (typically an API)
    when using Flask.

    Usage::
        from sermos import Blueprint, ApiServices
        bp = Blueprint('api_routes', __name__, url_prefix='/api')

        @bp.route('/my-api-route')
        class ApiClass(MethodView):
            @require_access_key
            def post(self, payload: dict):
                return {}
    """

    @wraps(fn)
    def decorated_view(*args, **kwargs):
        access_key = request.headers.get("accesskey")
        if not access_key:
            access_key = request.args.get("accesskey")

        configured_access_key = os.environ.get("API_ACCESS_KEY", None)

        if access_key == configured_access_key:
            return fn(*args, **kwargs)

        abort(HTTPStatus.UNAUTHORIZED)

    return decorated_view
