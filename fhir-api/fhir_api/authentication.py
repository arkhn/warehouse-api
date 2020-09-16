import os
from functools import wraps

import jwt
from flask import request

from errors import AuthenticationError

AUTH_DISABLED = True if os.getenv("AUTH_DISABLED", "").lower() in ["1", "true", "yes"] else False
JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY", "").replace("\\n", "\n")

if not AUTH_DISABLED and not JWT_PUBLIC_KEY:
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
            jwt.decode(token, JWT_PUBLIC_KEY, algorithms=["ES256"])
        except jwt.DecodeError:
            raise AuthenticationError("Failed to verify token.")

        return f(*args, **kwargs)

    return f if AUTH_DISABLED else decorated_function
