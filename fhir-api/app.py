import json

from flask import Flask, Blueprint, request, jsonify

from models import resources_models
from errors.operation_outcome import OperationOutcome

api = Blueprint('api', __name__)


@api.route("/<resource_type>/<id>", methods=['GET'])
def read(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome('Unknown resource type')

    Model = resources_models[resource_type]
    m = Model(id).read()
    if not m.resource:
        raise OperationOutcome(f"No {resource_type} matching id {id}")

    return m.json()


@api.route("/<resource_type>/<id>", methods=['PUT'])
def update(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome('Unknown resource type')

    Model = resources_models[resource_type]
    resource_data = request.get_json(force=True)
    if resource_data.get('id') != id:
        raise OperationOutcome('Resource id and update \
payload do not match')
    m = Model(id).update(resource_data)

    return m.json()


@api.route("/<resource_type>/<id>", methods=['PATCH'])
def patch(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome('Unknown resource type')

    Model = resources_models[resource_type]
    patch_data = request.get_json(force=True)
    if patch_data.get('id') != id:
        raise OperationOutcome('Resource id and update \
payload do not match')
    m = Model(id).patch(patch_data)

    return m.json()


@api.route("/<resource_type>", methods=['POST'])
def create(resource_type):
    if resource_type not in resources_models:
        raise OperationOutcome('Unknown resource type')

    Model = resources_models[resource_type]
    resource_data = request.get_json(force=True)
    m = Model(resource=resource_data).create()

    return m.json()


@api.route("/<resource_type>/<id>", methods=['DELETE'])
def delete(resource_type, id):
    if resource_type not in resources_models:
        raise OperationOutcome('Unknown resource type')

    Model = resources_models[resource_type]
    m = Model(id=id).delete()

    return m.json()


@api.route("/<resource_type>", methods=['GET'])
def search(resource_type):
    if resource_type not in resources_models:
        raise OperationOutcome('Unknown resource type')

    Model = resources_models[resource_type]
    results = Model(id).search(request.args)

    if not results:
        raise OperationOutcome(f"No {resource_type} matching search criterias")

    return jsonify(results)


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400


app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
