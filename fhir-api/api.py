from flask import Blueprint, request, jsonify
from jsonschema import ValidationError

from fhirstore import NotFoundError
from errors.operation_outcome import OperationOutcome
from models import resources_models
from subsearch.search import (
    process_params,
    resource_count,
    resource_search,
)

from flask_cors import CORS
from urllib.parse import parse_qs
from pandas import read_json, to_json, merge

api = Blueprint("api", __name__)
# enable Cross-Origin Resource Sharing
# "Allow-Control-Allow-Origin" HTTP header
CORS(api)


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

    processed_params, result_size, elements, is_summary_count, offset = process_params(
        search_args
    )
    Model = resources_models[resource_type]

    if is_summary_count:
        results = resource_count(Model, processed_params)
    else:
        results = resource_search(
            Model, processed_params, offset, result_size, elements
        )

    if not results:
        raise OperationOutcome(f"No {resource_type} matching search criterias")
    return jsonify(results)


def search_from_url_to_json(resource_type, url_args):
    if resource_type not in resources_models:
        raise OperationOutcome("Unknown resource type")

    search_args = parse_qs(url_args)

    processed_params, result_size, elements, is_summary_count, offset = process_params(
        search_args
    )
    Model = resources_models[resource_type]

    if is_summary_count:
        results = resource_count(Model, processed_params)
    else:
        results = resource_search(
            Model, processed_params, offset, result_size, elements
        )

    if not results:
        raise OperationOutcome(f"No {resource_type} matching search criterias")
    return read_json(jsonify(results), orient="records")


@api.route("/t2a", methods=["GET"])
def t2a(start_chemo, end_chemo):

    products = search_from_url_to_json(
        "MedicinalProductPharmaceutical",
        "administrableDoseForm=gt0&_element=characteristics,ingredient,status,identifier,administrableDoseForm",
    )
    medicationrequest = search_from_url_to_json(
        "MedicationRequest",
        f"performedOn=gt{start_chemo}&performedOn=lt{end_chemo}&_element=detectedIssue,authoredOn,identifier,SupportingInformation,status,priorRequest,basedOn,performedOn",
    )
    medicationadministration = search_from_url_to_json(
        "MedicationAdministration",
        f"datetime=gt{start_chemo}&datetime=lt{end_chemo}&_element=dosage,datetime",
    )
    episodeofcare = search_from_url_to_json("EpisodeOfCare", "_element=period.start")
    patient = search_from_url_to_json(
        "Patient", "_element=identifier.value&subject.identifier.value"
    )
    organization = search_from_url_to_json("Organization", "_element=identifier,partOf")

    ##group Patient, Episode of care and organization together
    # key1 and 2 not named the same
    group1 = merge(
        medicationrequest,
        organization,
        left_on=["supportingInformation.identifier.value"],
        right_on=["identifier.value"],
        how="left",
    )
    group2 = merge(
        group1,
        products,
        left_on=["medication.medicationReference.identifier.value"],
        right_on=["ingredient.ingredient.identifier.value"],
        how="left",
    )
    group3 = merge(
        episodeofcare,
        patient,
        left_on=["subject.identifier.value"],
        right_on=["identifier.value"],
        how="left",
    )
    group4 = merge(
        medicationadministration,
        group3,
        left_on=["subject.identifier.value"],
        how="left",
    )
    final = merge(
        group4,
        group2,
        left_on=["request.identifier.value"],
        right_on=["identifier.value"],
        how="outer",
    )
    
    # final.groupby("")

    return final.to_json


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400
