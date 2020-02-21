from collections import defaultdict
from fhirstore import NotFoundError
from errors.operation_outcome import OperationOutcome
import elasticsearch


def parse_comma(key, value):

    has_comma = "," in value
    if has_comma:
        return "multiple", {key: value.split(",")}
    else:
        return key, [value]


def sub_search(search_args):
    parsed_params = defaultdict(list)

    if search_args == {}:
        return {}

    for key, value in search_args.items():
        if len(value) == 1:
            element_key, parsed_element = parse_comma(key, value[0])
            parsed_params[element_key] = parsed_element
        else:
            for element in value:
                element_key, parsed_element = parse_comma(key, element)
                if element_key == "multiple":
                    parsed_params[element_key] = parsed_element
                else:
                    parsed_params[element_key].append(parsed_element[0])
    return parsed_params


def result_params(parsed_params):
    total = 100
    elements = None
    count = None
    if parsed_params.get("_count"):
        total = int(parsed_params.pop("_count")[0])

    if parsed_params.get("_element"):
        elements = parsed_params.pop("_element")
    elif parsed_params.get("multiple") and parsed_params["multiple"].get("_element"):
        elements = parsed_params["multiple"].pop("_element")

    if parsed_params.get("_summary"):
        if parsed_params["_summary"] == "false":
            parsed_params.pop("_summary")
        elif parsed_params["_summary"] == "text":
            parsed_params.pop("_summary")
            elements = ["text", "id", "meta"]
        elif parsed_params["_summary"] == "count":
            count = True

    return parsed_params, total, elements, count


def error_handler_count(Model, processed_params):
    try:
        return Model(id).count(processed_params)
    except elasticsearch.exceptions.NotFoundError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.RequestError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.AuthenticationException as e:
        raise OperationOutcome(e)


def error_handler_search(Model, processed_params, offset, total, elements):
    try:
        return Model(id).search(processed_params, offset, total, elements)
    except elasticsearch.exceptions.NotFoundError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.RequestError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.AuthenticationException as e:
        raise OperationOutcome(e)
