from functools import wraps

import requests
from flask import request

from fhir_api import settings
from fhir_api.errors import AuthenticationError


def validate_token(token, scope=None):
    payload = {"token": token}
    if scope is not None:
        payload["scope"] = scope

    response = requests.post(settings.TOKEN_INTROSPECTION_URL, data=payload)

    validation = response.json()

    return validation["active"]


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        prefix = "Bearer "
        if not auth_header.startswith(prefix):
            raise AuthenticationError("Authorization header malformed or unexisting.")

        token = auth_header[len(prefix) :]

        if not validate_token(token):
            raise AuthenticationError("Failed to verify token.")

        return f(*args, **kwargs)

    return f if settings.AUTH_DISABLED else decorated_function
