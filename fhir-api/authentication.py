from flask import request
from functools import wraps
import os
import requests

from errors import AuthenticationError

TOKEN_INTROSPECTION_URL = os.getenv("TOKEN_INTROSPECTION_URL")
AUTH_DISABLED = True if os.getenv("AUTH_DISABLED", "").lower() in ["1", "true", "yes"] else False


def validate_token(token, scope=None):
    payload = {"token": token}
    if scope is not None:
        payload["scope"] = scope

    response = requests.post(TOKEN_INTROSPECTION_URL, data=payload)

    validation = response.json()

    return validation["active"]


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        prefix = "Bearer "
        if not auth_header.startswith(prefix):
            raise AuthenticationError("Authorization header malformed or unexisting.")

        token = auth_header[len(prefix):]

        if not validate_token(token):
            raise AuthenticationError("Failed to verify token.")

        return f(*args, **kwargs)

    return f if AUTH_DISABLED else decorated_function
