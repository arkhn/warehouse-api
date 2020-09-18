import glob

import click
from bson import ObjectId
from flask import Flask, json

from fhir_api import db, models
from fhir_api.api import api


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def create_app():
    # Check for environment variables
    app = Flask(__name__)
    app.register_blueprint(api)
    app.json_encoder = JSONEncoder

    # load fhirstore at application startup
    db.get_store()
    # initialize models
    models.init()

    return app


app = create_app()


@app.cli.command()
@click.argument("src-dir", type=click.Path(exists=True))
def load_defs(src_dir):
    """Load FHIR definitions.

    SRC_DIR is a path to the definitions directory.
    """
    store = db.get_store()

    for bundle in glob.glob(f"{src_dir}/*.json"):
        with open(bundle, "r") as raw_data:
            store.upload_bundle(json.load(raw_data))
