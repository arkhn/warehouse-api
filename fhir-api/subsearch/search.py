from collections import defaultdict
from errors.operation_outcome import OperationOutcome
import elasticsearch
import re
import logging


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


def sort_params(parsed_params):
    sort = None
    if "_sort" in parsed_params:
        sort = parsed_params["_sort"]
    elif "multiple" in parsed_params:
        sort = parsed_params["multiple"].get("_sort", None)
    # if there is a sorting argument, process it to handle a change of sorting order
    if sort:
        sorting_params = []
        for argument in sort:
            # find a "-" before the argument. It indicates a sorting order different from default
            has_minus = re.search(r"^-(.*)", argument)
            if has_minus:
                # if the argument is -score, sort by ascending order (i.e. ascending relevance)
                if has_minus.group(1) == "_score":
                    sorting_params.append({has_minus.group(1): {"order": "asc"}})
                # for any other argument, sort by descending order
                else:
                    sorting_params.append({has_minus.group(1): {"order": "desc"}})
            # if there is no "-", use order defaults defined in elasticsearch
            else:
                sorting_params.append(argument)
        return sorting_params
    else:
        return None


def include_params(parsed_params):

    included = None
    if "_include" in parsed_params:
        try:
            included = [re.search(r"(.*):(.*)", parsed_params["_include"][0]).group(2)]
        except AttributeError:
            raise OperationOutcome(f"_include must be of format Resource:attribute")

    elif "multiple" in parsed_params and parsed_params["multiple"].get("_include", None):
        attributes = parsed_params["multiple"].get("_include", None)
        try:
            included = [re.search(r"(.*):(.*)", elem).group(2) for elem in attributes]
        except AttributeError:
            raise OperationOutcome(f"_include must be of format Resource:attribute")

    return included


def clean_params(parsed_params):
    if "multiple" in parsed_params:
        parsed_params["multiple"].pop("_element", None)
        parsed_params["multiple"].pop("_sort", None)
        parsed_params["multiple"].pop("_include", None)

    if parsed_params.get("multiple") == {}:
        parsed_params = {}

    parsed_params.pop("_summary", None)
    parsed_params.pop("_element", None)
    parsed_params.pop("_sort", None)
    parsed_params.pop("_include", None)

    return parsed_params


def process_params(search_args):

    parsed_params = parse_params(search_args)
    # TODO: handle offset
    offset = 0
    elements = None
    sort = sort_params(parsed_params)
    include = include_params(parsed_params)
    result_size = parsed_params.pop("_count", None)
    result_size = int(result_size[0]) if result_size else 100
    is_summary_count = "_summary" in parsed_params and parsed_params["_summary"][0] == "count"

    if "_summary" in parsed_params and parsed_params["_summary"][0] == "text":
        elements = ["text", "id", "meta"]
    elif "_element" in parsed_params:
        elements = parsed_params["_element"]
    elif "multiple" in parsed_params:
        elements = parsed_params["multiple"].get("_element", None)

    cleaned_params = clean_params(parsed_params)

    return cleaned_params, result_size, elements, is_summary_count, offset, sort, include


def resource_count(Model, processed_params):
    try:
        return Model(id).count(processed_params)
    except elasticsearch.exceptions.NotFoundError as e:
        logging.warning(f"{e.info['error']['index']} is not indexed in the database yet.")
    except elasticsearch.exceptions.RequestError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.AuthenticationException as e:
        raise OperationOutcome(e)


def resource_search(Model, processed_params, result_size, elements, offset, sort, include):
    try:
        return Model(id).search(processed_params, result_size, elements, offset, sort, include)
    except elasticsearch.exceptions.NotFoundError as e:
        logging.warning(f"{e.info['error']['index']} is not indexed in the database yet.")
    except elasticsearch.exceptions.RequestError as e:
        raise OperationOutcome(e)
    except elasticsearch.exceptions.AuthenticationException as e:
        raise OperationOutcome(e)
