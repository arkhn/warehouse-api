from flask import request
from functools import wraps
import jwt
import os

from errors import AuthenticationError

JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        prefix = "Bearer "
        if not auth_header.startswith(prefix):
            raise AuthenticationError("Authorization header malformed or unexisting.")

        token = auth_header[len(prefix):]

        try:
            jwt.decode(token, JWT_PUBLIC_KEY, algorithms=["AES256"])
        except jwt.DecodeError:
            raise AuthenticationError("Failed to verify token.")

        return f(*args, **kwargs)

    return decorated_function
