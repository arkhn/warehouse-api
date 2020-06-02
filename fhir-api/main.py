from bson import ObjectId
from flask import Flask, json
import os

from api import api
import db
import models


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def create_app():
    # Check for environment variables
    if "JWT_PUBLIC_KEY" not in os.environ:
        raise EnvironmentError("JWT_PUBLIC_KEY env variable doesn't exist.")

    app = Flask(__name__)
    app.register_blueprint(api)
    app.json_encoder = JSONEncoder

    # load fhirstore at application startup
    db.get_store()
    # initialize models
    models.init()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")
