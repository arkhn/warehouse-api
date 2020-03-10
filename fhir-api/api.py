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
from pandas import json_normalize, merge, DataFrame
import json


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
    return json_normalize(jsonify(results), max_level=3)


def stringToInt(x):
    try:
        return int(float(x))
    except ValueError:  # occurs when x is NaN
        return -1


@api.route("/t2a", methods=["GET"])
def t2a(start_chemo, end_chemo, limit=10):
    args = {key: request.args.getlist(key) for key in request.args.keys()}
    start_chemo = args["start"]
    end_chemo = args["end"]
    limit = args["limit"]
    products = search_from_url_to_json(
        "MedicinalProductPharmaceutical",
        "administrableDoseForm=gt0&_element=characteristics,ingredient,status,identifier,administrableDoseForm",
    )
    medicationrequest = search_from_url_to_json(
        "MedicationRequest", f"identifier.value=gt200000&_count=3000",
    )
    medicationadministration = search_from_url_to_json(
        "MedicationAdministration", f"_count=3000&request.identifier.value=gt200000",
    )
    episodeofcare = search_from_url_to_json("EpisodeOfCare", "_count=3000")
    patient = search_from_url_to_json(
        "Patient", "_count=3000&_element=identifier.value&subject.identifier.value"
    )
    organization = search_from_url_to_json("Organization", "_element=identifier,partOf")

    episodeofcare_parsed = [
        {
            "patient.identifier": stringToInt(x["patient"]["identifier"]["value"]),
            "period.start": x["period"]["start"],
        }
        for x in episodeofcare["items"]
        if stringToInt(x["patient"]["identifier"]["value"]) >= 0
    ]

    medicationadministration_parsed = [
        {
            "dosage.dose.value": x["dosage"]["dose"]["value"],
            "date_dispensation": x["effectiveDateTime"],
            "medication.dci": stringToInt(
                x["medicationReference"]["identifier"]["value"]
            ),
            "medicationrequest.identifier": stringToInt(
                x["request"]["identifier"]["value"]
            ),
            "patient.identifier.value": stringToInt(
                x["subject"]["identifier"]["value"]
            ),
        }
        for x in medicationadministration["items"]
        if stringToInt(x["subject"]["identifier"]["value"]) >= 0
        and stringToInt(x["request"]["identifier"]["value"]) >= 0
        and stringToInt(x["medicationReference"]["identifier"]["value"]) >= 0
    ]

    medicationrequest_parsed = [
        {
            "basedon.identifier": stringToInt(x["basedOn"][0]["identifier"]["value"]),
            "identifier.value": stringToInt(x["identifier"][0]["value"]),
            "status": x["status"],
            "medication.dci": stringToInt(
                x["medicationReference"]["identifier"]["value"]
            ),
            "priorRequest.identifier.value": stringToInt(
                x["priorPrescription"]["identifier"]["value"]
            ),
            "patient.identifier.value": stringToInt(
                x["subject"]["identifier"]["value"]
            ),
            "groupeService.identifier.value": stringToInt(
                x["supportingInformation"][0]["identifier"]["value"]
            ),
        }
        for x in medicationrequest["items"]
        if (
            stringToInt(x["basedOn"][0]["identifier"]["value"]) >= 0
            and stringToInt(x["identifier"][0]["value"]) >= 0
            and stringToInt(x["medicationReference"]["identifier"]["value"]) >= 0
            and stringToInt(x["supportingInformation"][0]["identifier"]["value"]) >= 0
            and stringToInt(x["subject"]["identifier"]["value"]) >= 0
            and stringToInt(x["priorPrescription"]["identifier"]["value"]) >= 0
        )
    ]

    organization_parsed = [
        {
            "identifier.SERVICE_PRE": stringToInt(
                x["identifier"][0].get("value", "-2")
            ),  # json is broken. If error --> return -1
            "identifier.CODE1_SERVICE_EX": stringToInt(
                x["identifier"][2].get("value", "-2")
            ),  # json is broken. If error --> return -1
            "identifier.CODE2_SERVICE_EX": stringToInt(
                x["identifier"][1].get("value", "-2")
            ),  # json is broken. If error --> return -1
            "partOf.Organization": x["partOf"].get("identifier", {"value": "-1"})[
                "value"
            ],  # json is broken. If error --> return -1
        }
        for x in organization["items"]
        if (
            stringToInt(x["identifier"][0].get("value", "-1")) >= 0
            and stringToInt(x["identifier"][2].get("value", "-1")) >= 0
            # adding the following condition removes all elements:
            # and stringToInt(x['identifier'][1].get('value', '-1')) >= -1
        )
    ]

    patient_parsed = [
        {
            "identifier": stringToInt(x["identifier"][0]["value"]),
            "managingOrganization": x.get(
                "managingOrganization", {"identifier": {"value": "-2"}}
            )["identifier"][
                "value"
            ],  # json is broken. If managingOrganization does not exist --> return -1
        }
        for x in patient["items"]
        if stringToInt(x["identifier"][0]["value"]) >= 0
    ]

    products_parsed = [
        {
            "administrableDoseForm.DOSAGE": x["administrableDoseForm"]["coding"][0][
                "code"
            ],
            "characteristics.T2A": x["characteristics"][0]["code"]["coding"][0]["code"],
            "characteristics.ATU_T2A": x["characteristics"][0]["status"]["coding"][0][
                "code"
            ],
            "identifier.numero_lot": stringToInt(x["identifier"][0]["value"]),
            "identifier.UCDcode": stringToInt(x["identifier"][1]["value"]),
            "identifier.nompdt": stringToInt(x["identifier"][2]["value"]),
            "ingredient.DCI": stringToInt(x["ingredient"][0]["identifier"]["value"]),
        }
        for x in products["items"]
        if (
            stringToInt(x["identifier"][0]["value"]) >= 0
            and stringToInt(x["ingredient"][0]["identifier"]["value"]) >= 0
            # adding the following conditions removes all elements:
            # and stringToInt(x['identifier'][1]['value']) >= 0
            # and stringToInt(x['identifier'][2]['value']) >= 0
        )
    ]

    episodeofcare_dataframe = DataFrame.from_dict(episodeofcare_parsed)
    medicationadministration_dataframe = DataFrame.from_dict(
        medicationadministration_parsed
    )
    medicationrequest_dataframe = DataFrame.from_dict(medicationrequest_parsed)
    organization_dataframe = DataFrame.from_dict(organization_parsed)
    patient_dataframe = DataFrame.from_dict(patient_parsed)
    products_dataframe = DataFrame.from_dict(products_parsed)

    ##group Patient, Episode of care and organization together
    # key1 and 2 not named the same
    group1 = merge(
        medicationrequest_dataframe,
        organization_dataframe,
        left_on=["groupeService.identifier.value"],
        right_on=["identifier.SERVICE_PRE"],
        how="left",
    )
    group2 = merge(
        group1,
        products_dataframe,
        left_on=["medication.dci"],
        right_on=["ingredient.DCI"],
        how="left",
    )
    group3 = merge(
        episodeofcare_dataframe,
        patient_dataframe,
        left_on=["patient.identifier"],
        right_on=["identifier"],
        how="left",
    )
    group4 = merge(
        medicationadministration_dataframe,
        group3,
        left_on=["patient.identifier.value"],
        right_on=["patient.identifier"],
        how="left",
    )
    final = merge(
        group4, 
        group2,
        left_on=["medicationrequest.identifier"],
        right_on=["basedon.identifier"],
        how="left",
    )

    return final[:limit].to_dict(orient="records")


@api.errorhandler(OperationOutcome)
def handle_bad_request(e):
    return str(e), 400
