import logging
import os
import re
# import json
# import requests
import math

import elasticsearch
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from jsonschema import ValidationError

from fhirstore import NotFoundError
from fhirstore.search import SearchArguments, Bundle

from authentication import auth_required
from db import get_store
from errors import OperationOutcome, AuthenticationError
from models import resources_models
from fhir2ecrf import FHIR2eCRF

# from arkhn_arx import Anonymizer

from pysin import search as document_search

FHIR_API_URL = os.getenv("FHIR_API_URL")
FHIR_API_TOKEN = os.getenv("FHIR_API_TOKEN")
ARX_HOST = os.getenv("ARX_HOST")
ARX_PORT = os.getenv("ARX_PORT")

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

    # FIXME clean all of this
    if resource_type == "Group" and "$export" in request.args:
        f = FHIR2eCRF(FHIR_API_TOKEN, f"{FHIR_API_URL}/")
        params = request.get_json(force=True)
        df = f.query(params)
        # try:
        #     df, score = Anonymizer(f"{ARX_HOST}:{ARX_PORT}").anonymize_dataset(df, params)
        # except requests.exceptions.RequestException as e:
        #     return jsonify({"error": json.loads(str(e))})

        # TODO anonymize dataset
        # return jsonify({"df": df.to_dict(orient="list"), "score": score[0]})
        df = df.replace({math.nan: None})
        return jsonify({"df": df.to_dict(orient="list"), "score": 0})

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
    bundle = Bundle()

    if resource_type not in resources_models:
        bundle.fill_error(diagnostic=f"Unknown resource type: {resource_type}")
        return jsonify(bundle.content)
    search_args = SearchArguments()
    search_args.parse(request.args, resource_type)

    # FIXME cleanup
    if resource_type == "DocumentReference" and request.args.get("$search"):
        key_word = request.args.get("$search")
        results, count_dict = document_search(key_word, os.environ.get("DOCUMENTS_PATH"))
        document_names = []
        contexts = []
        for result in results[1:]:  # remove the header
            path, _, context = result
            document_name = re.search(r"\d+\.pdf", path).group(0)
            document_names.append(document_name)
            contexts.append(context)

        store = get_store()
        document_references = store.db[resource_type].find(
            {"content.attachment.url": {"$in": document_names}}
        )

        entries = []
        for document_reference, context in zip(document_references, contexts):
            del document_reference["_id"]
            document_reference["description"] = context
            entries.append({"resource": document_reference, "search": {"mode": "match"}})
        bundle.content["entry"] = entries
        bundle.content["total"] = count_dict["nb"]

        return jsonify(bundle.content)

    Model = resources_models[resource_type]
    try:
        bundle.complete(Model(id).search(request.args), search_args.formatting_args)

    except elasticsearch.exceptions.NotFoundError as e:
        bundle.fill_error(
            diagnostic=f"{e.info['error']['index']} is not indexed in the database yet."
        )
    except elasticsearch.exceptions.RequestError as e:
        bundle.fill_error(diagnostic=e.info["error"]["root_cause"])
    except elasticsearch.exceptions.AuthenticationException as e:
        bundle.fill_error(diagnostic=e.info["error"]["root_cause"])

    if "entry" in bundle.content and bundle.content["total"] == 0:
        error_bundle = Bundle()
        error_bundle.fill_error(
            severity="warning",
            code="not-found",
            details=f"No {resource_type} matching search criteria",
        )
        bundle.content["entry"].append({"resource": error_bundle.content})

    return jsonify(bundle.content)


@api.route("/", methods=["GET"])
@auth_required
def search_multiple_resources():
    bundle = Bundle()
    if not request.args.get("_type"):
        bundle.fill_error(
            code="structure",
            diagnostic="No resource provided in _type parameter",
            details="Search across all resource types is not handled yet",
        )
        return jsonify(bundle.content)

    resources = request.args["_type"].split(",")
    if len(resources) < 1:
        bundle.fill_error(
            code="structure", diagnostic="Provide at least one resource in _type parameter"
        )
        return jsonify(bundle.content)

    search_args = SearchArguments()
    # initiate the search args with the first resource provided
    search_args.parse(request.args, resources[0])

    for resource_type in resources:
        if resource_type not in resources_models:
            bundle.fill_error(diagnostic=f"Unknown resource type: {resource_type}")
        else:
            Model = resources_models[resource_type]
            try:
                bundle.complete(Model(id).search(request.args), search_args.formatting_args)
            except elasticsearch.exceptions.NotFoundError as e:
                logging.warning(f"{e.info['error']['index']} is not indexed in the database yet.")
            except elasticsearch.exceptions.RequestError as e:
                bundle.fill_error(code="structure", diagnostic=e.info["error"]["root_cause"])
            except elasticsearch.exceptions.AuthenticationException as e:
                bundle.fill_error(code="login", diagnostic=e.info["error"]["root_cause"])

    if "entry" in bundle.content and bundle.content["total"] == 0:
        error_bundle = Bundle()
        error_bundle.fill_error(
            severity="warning",
            code="not-found",
            details=f"No {resource_type} matching search criteria",
        )
        bundle.content["entry"].append({"resource": error_bundle.content})

    return jsonify(bundle.content)


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
