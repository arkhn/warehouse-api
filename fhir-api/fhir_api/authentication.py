from functools import wraps

import jwt
from flask import request

from fhir_api import settings
from fhir_api.errors import AuthenticationError

if not settings.AUTH_DISABLED and not settings.JWT_PUBLIC_KEY:
    raise Exception("missing JWT_PUBLIC_KEY")


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        prefix = "Bearer "
        if not auth_header.startswith(prefix):
            raise AuthenticationError("Authorization header malformed or unexisting.")

        token = auth_header[len(prefix) :]

        try:
            jwt.decode(token, settings.JWT_PUBLIC_KEY, algorithms=["ES256"])
        except jwt.DecodeError:
            raise AuthenticationError("Failed to verify token.")

        return f(*args, **kwargs)

    return f if settings.AUTH_DISABLED else decorated_function
