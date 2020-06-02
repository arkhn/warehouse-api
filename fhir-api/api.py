import logging
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from jsonschema import ValidationError

from fhirstore import NotFoundError

from authentication import auth_required
from db import get_store
from errors import OperationOutcome, AuthenticationError
from models import resources_models
from subsearch.search import (
    process_params,
    resource_count,
    resource_search,
)

api = Blueprint("api", __name__)
# enable Cross-Origin Resource Sharing
# "Allow-Control-Allow-Origin" HTTP header
CORS(api)


@api.route("/<resource_type>/<id>", methods=["GET"])
@auth_required
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
@auth_required
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
@auth_required
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
@auth_required
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
@auth_required
def delete(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")

    Model = resources_models[resource_type]
    m = Model(id=id).delete()

    return m.json()


@api.route("/<resource_type>", methods=["GET"])
@auth_required
def search(resource_type):
    if resource_type not in resources_models:
        raise OperationOutcome(f"Unknown resource type: {resource_type}")
    search_args = {key: request.args.getlist(key) for key in request.args.keys()}
    (
        processed_params,
        result_size,
        elements,
        is_summary_count,
        offset,
        sort,
        include,
    ) = process_params(search_args)
    Model = resources_models[resource_type]

    if is_summary_count:
        results = resource_count(Model, processed_params)
    else:
        results = resource_search(
            Model, processed_params, result_size, elements, offset, sort, include
        )
    if not results:
        raise OperationOutcome(f"No {resource_type} matching search criteria")
    return jsonify(results)


@api.route("/", methods=["GET"])
@auth_required
def search_multiple_resources():
    search_args = {key: request.args.getlist(key) for key in request.args.keys()}
    if not search_args.get("_type"):
        raise OperationOutcome("No resource provided in _type parameter")
    if "," not in search_args["_type"][0]:
        raise OperationOutcome("Provide more than one resource in _type parameter")

    resource_types = search_args.pop("_type")[0].split(",")
    (
        processed_params,
        result_size,
        elements,
        is_summary_count,
        offset,
        sort,
        include,
    ) = process_params(search_args)
    results = {"resource_type": "Bundle", "total": 0, "entry": []}
    for resource in resource_types:
        Model = resources_models[resource]
        if is_summary_count:
            result_per_resource = resource_count(Model, processed_params)
        else:
            result_per_resource = resource_search(
                Model, processed_params, result_size, elements, offset, sort, include
            )
        if not result_per_resource:
            continue

        results["total"] += result_per_resource["total"]
        results["entry"] += result_per_resource.get("entry")
        if "tag" not in results:
            results["tag"] = result_per_resource.get("tag")

    if not results:
        raise OperationOutcome(f"No {resource_types} matching search criteria")
    return jsonify(results)


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


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400


@api.errorhandler(AuthenticationError)
def handle_not_authorized(e):
    return str(e), 401
