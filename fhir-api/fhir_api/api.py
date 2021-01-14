import logging
import os

from fhir.resources.operationoutcome import OperationOutcome
from flask import Blueprint, jsonify, request
from flask_cors import CORS

from fhir_api.authentication import auth_required
from fhir_api.db import get_store
from fhir_api.errors import AuthenticationError, BadRequest
from fhir_api.models import resources_models

# from fhir2ecrf import FHIR2eCRF

# from arkhn_arx import Anonymizer

# FHIR_API_URL = os.getenv("FHIR_API_URL")
# FHIR_API_TOKEN = os.getenv("FHIR_API_TOKEN")
# ARX_HOST = os.getenv("ARX_HOST")
# ARX_PORT = os.getenv("ARX_PORT")

api = Blueprint("api", __name__, static_folder=".")
# enable Cross-Origin Resource Sharing
# "Allow-Control-Allow-Origin" HTTP header
CORS(api)

# fhir2ecrf = FHIR2eCRF(FHIR_API_TOKEN, f"{FHIR_API_URL}/")
# anonymizer = Anonymizer(f"{ARX_HOST}:{ARX_PORT}")


@api.route("/<resource_type>/<id>", methods=["GET"])
@auth_required
def read(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    model = resources_models[resource_type](id=id)

    return model.read().json()


@api.route("/<resource_type>/<id>", methods=["PUT"])
@auth_required
def update(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    resource_data = request.get_json(force=True)
    model = resources_models[resource_type](id=id)
    return model.update(resource_data).json()


@api.route("/<resource_type>/<id>", methods=["PATCH"])
@auth_required
def patch(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    patch_data = request.get_json(force=True)
    model = resources_models[resource_type](id=id)
    return model.patch(patch_data).json()


@api.route("/<resource_type>", methods=["POST"])
@auth_required
def create(resource_type):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    resource_data = request.get_json(force=True)

    model = resources_models[resource_type](resource=resource_data)
    return model.create().json()


@api.route("/<resource_type>/<id>", methods=["DELETE"])
@auth_required
def delete(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    model = resources_models[resource_type](id=id)
    return model.delete().json()


@api.route("/", methods=["GET"])
@api.route("/<resource_type>", methods=["GET"])
@auth_required
def search(resource_type=None):
    return get_store().search(
        resource_type, query_string=request.query_string.decode("utf-8"), as_json=True
    )


@api.route("/list-collections", methods=["GET"])
@auth_required
def list_collections():
    return jsonify(list(resources_models.keys()))


@api.route("/upload-bundle", methods=["POST"])
@auth_required
def upload_bundle():
    # TODO methodology to avoid/process huge bundles
    bundle_data = request.get_json(force=True)

    if "resourceType" not in bundle_data or bundle_data["resourceType"] != "Bundle":
        raise OperationOutcome("input must be a FHIR Bundle resource")

    store = get_store()
    try:
        store.upload_bundle(bundle_data)
    except Exception as e:
        logging.error(f"Error while uploading bundle: {e}")
        return jsonify(success=False)

    return jsonify(success=True)


@api.route("/metadata", methods=["GET"])
@auth_required
def capabilities():
    return api.send_static_file("capabilities.json")


@api.errorhandler(BadRequest)
def handle_bad_request(e):
    operation_outcome = OperationOutcome(
        issue=[{"severity": "error", "code": "invalid", "diagnostics": str(e)}]
    )
    return jsonify(operation_outcome.dict()), 400


@api.errorhandler(AuthenticationError)
def handle_not_authorized(e):
    return str(e), 401


@api.route("/version/", methods=["GET"])
def version():
    data = {
        "commit": os.environ.get("VERSION_SHA", "") or None,
        "version": os.environ.get("VERSION_NAME", "") or None,
    }
    return jsonify(data)
