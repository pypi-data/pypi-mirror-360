import json

from fuzzywuzzy import fuzz, process


def enum_standardize(
    dfObj,
    enumObj,
    column_name,
    thresh=70,
    manual_changes={},
    identifier="None",
    scorer=fuzz.token_sort_ratio,
):
    """Standardize Column based on enum vaues

    Args:
        dfObj (_type_): _description_
        enumObj (_type_): _description_
        column_name (_type_): _description_
        e (_type_): _description_
        thresh (int, optional): _description_. Defaults to 70.
        manual_changes (dict, optional): _description_. Defaults to {}.
        identifier (str, optional): _description_. Defaults to "None".

    Returns:
        _type_: _description_
    """

    proper_name = [name.value for name in enumObj]

    improper_name = dfObj[column_name].tolist()
    improper_name = list(set(improper_name))

    # Dictionaries will have key value pair as improper and proper name
    logs = {}
    changes = {}
    corrupt = {}
    # will probably create filters for ratio
    for query in improper_name:
        match = process.extractOne(query.strip(), proper_name, scorer=scorer)
        if match[1] >= thresh:
            changes[query] = match[0]
        else:
            if query not in manual_changes.keys():
                corrupt[query] = ""

    changes.update(manual_changes)

    # Provide the corrupt_names.json at the same folder where script is
    if bool(corrupt):
        print(
            "There are improper names that function can't fix.\nPlease refer to logs.json."
        )

    logs.update({identifier: {"changes": changes, "corrupt": corrupt}})

    with open("enum_standardization.log", "a+") as log_file:
        log_file.write(json.dumps(logs) + "\n")

    # replacing values that needs to be changes only to specific column
    dfObj = dfObj.replace({column_name: changes})

    return dfObj
