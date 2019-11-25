from flask import Blueprint, request, jsonify
from jsonschema import ValidationError

from fhirstore import NotFoundError
from errors.operation_outcome import OperationOutcome
from models import resources_models

api = Blueprint("api", __name__)


@api.route("/<resource_type>/<id>", methods=["GET"])
def read(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome("Unknown resource type")

    Model = resources_models[resource_type]
    try:
        m = Model(id).read()
    except NotFoundError:
        raise OperationOutcome(f"No {resource_type} matching id {id}")

    return m.json()


@api.route("/<resource_type>/<id>", methods=["PUT"])
def update(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome("Unknown resource type")

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
        raise OperationOutcome("Unknown resource type")

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
        raise OperationOutcome("Unknown resource type")

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
        raise OperationOutcome("Unknown resource type")

    Model = resources_models[resource_type]
    m = Model(id=id).delete()

    return m.json()


@api.route("/<resource_type>", methods=["GET"])
def search(resource_type):
    if resource_type not in resources_models:
        raise OperationOutcome("Unknown resource type")

    Model = resources_models[resource_type]
    results = Model(id).search(request.args)

    if not results:
        raise OperationOutcome(f"No {resource_type} matching search criterias")

    return jsonify(results)


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400
