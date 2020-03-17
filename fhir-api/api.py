import logging
from flask import Blueprint, request, jsonify
from jsonschema import ValidationError

from fhirstore import NotFoundError

from db import get_store
from errors.operation_outcome import OperationOutcome
from models import resources_models
from subsearch.search import (
    process_params,
    resource_count,
    resource_search,
)

from flask_cors import CORS

api = Blueprint("api", __name__)
# enable Cross-Origin Resource Sharing
# "Allow-Control-Allow-Origin" HTTP header
CORS(api)


@api.route("/<resource_type>/<id>", methods=["GET"])
def read(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    Model = resources_models[resource_type]
    try:
        m = Model(id).read()
    except NotFoundError:
        raise OperationOutcome(f"No {resource_type} matching id {id}")

    return m.json()


@api.route("/<resource_type>/<id>", methods=["PUT"])
def update(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    Model = resources_models[resource_type]
    resource_data = request.get_json(force=True)

    try:
        m = Model(id).update(resource_data)
    except ValidationError as e:
        raise OperationOutcome(e.message)

    return m.json()


@api.route("/<resource_type>/<id>", methods=["PATCH"])
def patch(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    Model = resources_models[resource_type]
    patch_data = request.get_json(force=True)

    try:
        m = Model(id).patch(patch_data)
    except ValidationError as e:
        raise OperationOutcome(e.message)

    return m.json()


@api.route("/<resource_type>", methods=["POST"])
def create(resource_type):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    Model = resources_models[resource_type]
    resource_data = request.get_json(force=True)

    try:
        m = Model(resource=resource_data).create()
    except ValidationError as e:
        raise OperationOutcome(e.message)

    return m.json()


@api.route("/<resource_type>/<id>", methods=["DELETE"])
def delete(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    Model = resources_models[resource_type]
    m = Model(id=id).delete()

    return m.json()


@api.route("/<resource_type>", methods=["GET"])
def search(resource_type):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    search_args = {key: request.args.getlist(key) for key in request.args.keys()}

    processed_params, result_size, elements, is_summary_count, offset = process_params(search_args)
    Model = resources_models[resource_type]

    if is_summary_count:
        results = resource_count(Model, processed_params)
    else:
        results = resource_search(Model, processed_params, offset, result_size, elements)

    if not results:
        raise OperationOutcome(f"No {resource_type} matching search criterias")
    return jsonify(results)


@api.route("/upload-bundle", methods=["POST"])
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


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400
