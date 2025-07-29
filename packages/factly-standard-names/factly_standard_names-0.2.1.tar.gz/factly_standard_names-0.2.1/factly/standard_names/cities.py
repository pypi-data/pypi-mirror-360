import json

from fuzzywuzzy import fuzz, process

from .utils import get_std_names


def airline_city_names(
    dfObj, column_name, thresh=70, manual_changes={}, identifier="None"
):
    """
    find all improper airline city names from a given dataframe
    and replaces it with standard names proved.
    dfObj : DataFrame object on which airline city name should be standardize
    column_name : name of column which has entries as airline city name
    manual_changes = Dict , default : null dict , changes in names done manually.
    """

    proper_name = get_std_names(filter="city")
    proper_name = [name.strip() for name in proper_name]

    improper_name = dfObj[column_name].tolist()
    improper_name = list(set(improper_name))

    # Dictionaries will have key value pair as improper and proper name
    logs = {}
    changes = {}
    corrupt = {}
    # will probably create filters for ratio
    for query in improper_name:
        match = process.extractOne(
            query.strip(), proper_name, scorer=fuzz.token_set_ratio
        )
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

    with open("standard_names.log", "a+") as log_file:
        log_file.write(json.dumps(logs) + "\n")

    # replacing values that needs to be changes only to specific column
    dfObj = dfObj.replace({column_name: changes})

    return dfObj
