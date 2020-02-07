from flask import Blueprint, request, jsonify
from jsonschema import ValidationError

from fhirstore import NotFoundError
from errors.operation_outcome import OperationOutcome
from models import resources_models
from subsearch.search import sub_search
import elasticsearch

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

    search_args = {key: request.args.getlist(key) for key in request.args.keys()}

    parsed_params = sub_search(search_args)
    offset = 0
    total = 100

    if parsed_params.get("_count"):
        # Here _count is removed from the arguments to parse
        # because it needs to exist outside the search query in elasticsearch
        total = int(parsed_params.pop("_count")[0])
    Model = resources_models[resource_type]
    try:
        results = Model(id).search(parsed_params, offset, total)
    except elasticsearch.exceptions.NotFoundError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.RequestError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.AuthenticationException as e:
        raise OperationOutcome(e)

    if not results:
        raise OperationOutcome(f"No {resource_type} matching search criterias")

    return jsonify(results)


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400
