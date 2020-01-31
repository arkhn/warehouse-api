from collections import defaultdict


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
