"""
Module providing tools for post-processing configuration files and dataframes
"""
from collections import defaultdict

CONFIG_MAPPING = {
    "alias": "from:alias",
    "resource_type": "from:resource_type",
    "select_expression": "select:jsonpath",
    "how": "join:how",
    "searchparam": "join:jsonpath",
    "alias_child": "join:alias_child",
    "jsonpath": "where:searchparamArkhn",
    "prefix": "where:prefix",
    "value": "where:value",
}


def create_config(df_keep, patients_id):
    from_dict = defaultdict()
    select_dict = defaultdict(list)
    join_dict = defaultdict(dict)
    where_dict = defaultdict(dict)

    for i in range(len(df_keep.index)):
        data_line = df_keep.iloc[i]
        infos = {key: data_line[col_name] for key, col_name in CONFIG_MAPPING.items()}

        jsonpath_search = "id"
        ids_values = get_id_patients(patients_id)
        where_dict["patient"][jsonpath_search] = ids_values

        from_dict = update_from_data_line(from_dict, infos["alias"], infos["resource_type"])

        select_dict = update_select_data_line(
            select_dict, infos["select_expression"], infos["alias"]
        )

        where_dict = update_where_data_line(
            where_dict,
            infos["how"],
            infos["alias_child"],
            infos["alias"],
            infos["searchparam"],
            infos["prefix"],
            infos["jsonpath"],
            infos["value"],
            ids_values,
        )

        join_dict = update_join_data_line(
            join_dict, infos["how"], infos["alias"], infos["alias_child"], infos["searchparam"]
        )

    config = {
        "from": dict(from_dict),
        "select": dict(select_dict),
        "join": dict(join_dict),
        "where": dict(where_dict),
    }
    return config


def update_join_data_line(join_dict, how, alias, alias_child, searchparam):
    if not isNaN(how):
        if alias not in list(join_dict[how].keys()):
            join_dict[how][alias] = dict()
        join_dict[how][alias][searchparam] = alias_child
    return join_dict


def update_where_data_line(
    where_dict, how, alias_child, alias, searchparam, prefix, jsonpath, value, ids_values
):
    if not isNaN(how):
        if alias_child == "patient":
            where_dict[alias][f"{searchparam}.reference"] = ids_values

    if not isNaN(jsonpath):
        if jsonpath not in list(where_dict[alias].keys()):
            where_dict[alias][jsonpath] = dict()
        if not isNaN(prefix):
            where_dict[alias][jsonpath][prefix] = value
        else:
            where_dict[alias][jsonpath] = value
    return where_dict


def update_select_data_line(select_dict, select_expression, alias):
    if not isNaN(select_expression):
        select_dict[alias].append(select_expression)
    return select_dict


def update_from_data_line(from_dict, alias, resource_type):
    if alias in list(from_dict.keys()):
        assert from_dict[alias] == resource_type, "There is a probleme of alias compabilities"
    else:
        from_dict[alias] = resource_type
    return from_dict


def get_id_patients(patients_id):
    ids_val = patients_id[0]
    for id in patients_id[1:]:
        ids_val = f"{ids_val},{id}"
    return ids_val


def isNaN(num):
    return num != num


def change_alias(string, alias_old, alias_new):
    if isinstance(string, str):
        string = string.replace(alias_old, alias_new)
    return string


def treatment_first(x):
    if isinstance(x, list):
        for i in x:
            if not isNaN(i):
                return i
        return x[0]
    else:
        return x


def treatment_bool(value):
    if isNaN(value):
        return 0
    else:
        return 1


def treatment_list(x):
    if isinstance(x, list):
        result = x[0]
        for value in x[1:]:
            result = f"{result}; {value}"
        return result
    else:
        return x
