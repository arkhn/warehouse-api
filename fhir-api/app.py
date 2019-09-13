import json

from flask import Flask, Blueprint, abort, request

from models.resources import resources

api = Blueprint('api', __name__)


@api.route("/<resource_type>/<id>", methods=['GET'])
def read(resource_type, id):
    if resource_type not in resources:
        abort(404, 'Unknown resource type')

    Model = resources[resource_type]
    m = None
    try:
        m = Model(id).read()
    except Exception as e:
        abort(400, str(e))

    if not m.resource:
        abort(404, f"No {resource_type} matching id {id}")

    return m.json()


@api.route("/<resource_type>/<id>", methods=['PUT'])
def update(resource_type, id):
    if resource_type not in resources:
        abort(404, 'Unknown resource type')

    Model = resources[resource_type]
    m = None
    try:
        resource_data = request.get_json(force=True)
        if resource_data.get('id') != id:
            raise Exception('Resource id and update payload do not match')
        m = Model(id).update(resource_data)
    except Exception as e:
        abort(400, str(e))

    return m.json()


@api.route("/<resource_type>/<id>", methods=['PATCH'])
def patch(resource_type, id):
    if resource_type not in resources:
        abort(404, 'Unknown resource type')

    Model = resources[resource_type]
    m = None
    try:
        patch_data = request.get_json(force=True)
        if patch_data.get('id') != id:
            raise Exception('Resource id and update payload do not match')
        m = Model(id).patch(patch_data)
    except Exception as e:
        abort(400, str(e))

    return m.json()


@api.route("/<resource_type>", methods=['POST'])
def create(resource_type):
    if resource_type not in resources:
        abort(404, 'Unknown resource type')

    Model = resources[resource_type]
    m = None
    try:
        resource_data = request.get_json(force=True)
        m = Model(resource=resource_data).create()
    except Exception as e:
        abort(400, str(e))

    return m.json()


@api.route("/<resource_type>/<id>", methods=['DELETE'])
def delete(resource_type, id):
    if resource_type not in resources:
        abort(404, 'Unknown resource type')

    Model = resources[resource_type]
    m = None
    try:
        m = Model(id=id).delete()
    except Exception as e:
        abort(400, str(e))

    return m.json()


app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
