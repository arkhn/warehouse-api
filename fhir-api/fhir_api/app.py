import glob
import logging

import click
from bson import ObjectId
from fhirpath.enums import FHIR_VERSION
from flask import Flask, json

from fhir_api import db, models
from fhir_api.api import api
from fhir_api.utils import write_es_mappings


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


def create_app():
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
def bootstrap():
    """Bootstrap mongo collections and elasticsearch indices"""
    store = db.get_store()
    if not store.initialized:
        logging.info("Bootstrapping store...")
        store.bootstrap()
        logging.info("Done!")
    else:
        logging.info("Store is already initialized, skipping.")


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


@app.cli.command()
def disable_json_validator():
    """Disable the mongo JSON schema validator for all collections"""
    store = db.get_store()
    for r in store.resources:
        logging.info(f"Disabling collection validator for resource {r}...")
        res = store.db.command({"collMod": r, "validator": {}})
        logging.info(f"Done! ({res})")


@app.cli.command()
def rebuild_es_index():
    """
    Deletes the elasticsearch index and re-creates it.
    Warning: all the documents in the index will be lost.
    """
    store = db.get_store()

    logging.info(f"Dropping ES index {store.search_engine.get_index_name()}...")
    store.reset(mongo=False, es=True)
    logging.info("Done!")

    logging.info("Rebuilding ES index...")
    store.search_engine.create_es_index()


@app.cli.command()
@click.argument("dest-dir", type=click.Path(exists=True))
def generate_es_mappings(dest_dir):
    mappings = write_es_mappings(FHIR_VERSION.R4, dest_dir)
    click.echo(
        f"Total {len(mappings)} files have been written to {dest_dir}",
        color=click.style("green"),
    )
