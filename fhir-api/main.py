from flask import Flask, json
from bson import ObjectId

from api import api
import db
import models


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(api, url_prefix="/api")
    app.json_encoder = JSONEncoder

    # load fhirstore at application startup
    db.get_store()
    # initialize models
    models.init()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0")
