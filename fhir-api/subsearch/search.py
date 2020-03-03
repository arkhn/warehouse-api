from collections import defaultdict
from errors.operation_outcome import OperationOutcome
import elasticsearch


def parse_comma(key, value):
    has_comma = "," in value
    if has_comma:
        return "multiple", {key: value.split(",")}
    else:
        return key, [value]


def parse_params(search_args):
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


def clean_params(parsed_params):
    if parsed_params.get("multiple"):
        parsed_params["multiple"].pop("_element", None)
    if parsed_params.get("multiple") == {}:
        parsed_params = {}

    parsed_params.pop("_summary", None)
    parsed_params.pop("_element", None)
    return parsed_params


def process_params(search_args):

    parsed_params = parse_params(search_args)
    # TODO: handle offset
    offset = 0
    elements = None

    result_size = parsed_params.pop("_count", None)
    result_size = int(result_size[0]) if result_size else 100
    is_summary_count = (
        True
        if parsed_params.get("_summary") and parsed_params["_summary"][0] == "count"
        else False
    )

    if parsed_params.get("_summary") and parsed_params["_summary"][0] == "text":
        elements = ["text", "id", "meta"]
    elif parsed_params.get("_element"):
        elements = parsed_params.get("_element")
    elif parsed_params.get("multiple"):
        elements = parsed_params["multiple"].get("_element", None)

    cleaned_params = clean_params(parsed_params)

    return cleaned_params, result_size, elements, is_summary_count, offset


def count_model(Model, processed_params):
    try:
        return Model(id).count(processed_params)
    except elasticsearch.exceptions.NotFoundError as e:
        raise OperationOutcome(
            f"{e.info['error']['index']} is not indexed in the database yet."
        )
    except elasticsearch.exceptions.RequestError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.AuthenticationException as e:
        raise OperationOutcome(e)


def search_model(Model, processed_params, offset, result_size, elements):
    try:
        return Model(id).search(processed_params, offset, result_size, elements)
    except elasticsearch.exceptions.NotFoundError as e:
        raise OperationOutcome(
            f"{e.info['error']['index']} is not indexed in the database yet."
        )
    except elasticsearch.exceptions.RequestError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.AuthenticationException as e:
        raise OperationOutcome(e)
