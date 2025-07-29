import json

from fuzzywuzzy import fuzz, process

from .utils import get_country_data


def get_std_cntry(country, data):
    """Helper function to get the standard country name from the DataFrame."""
    return data[data["country_name"] == country[0]]["standard_country_name"].values[0]


def get_best_match(query, proper_name, thresh, data, scorers):

    # match format : [(country_name, score), (country_name, score)]
    # check if score is greater than thresh and then check first 2 match difference is greater than 1
    # or both the matches are from same country
    for scorer in scorers:
        match = process.extract(query.strip(), proper_name, scorer=scorer)
        if match[0][1] >= thresh and (
            match[0][1] >= match[1][1] + 1
            or get_std_cntry(match[0], data) == get_std_cntry(match[1], data)
        ):
            return get_std_cntry(match[0], data)
    return None


def state_country_names(
    dfObj, column_name, thresh=80, manual_changes={}, identifier="None"
):
    """
    find all improper country names from a given dataframe
    and replaces it with standard names proved.
    dfObj : DataFrame object on which contries name should be standardize
    column_name : name of column which has entries as country name
    manual_changes = Dict , default : null dict , changes in names done manually.
    """

    data = get_country_data()  # gets the list of standard country names
    proper_name = [name.strip() for name in data["country_name"]]

    improper_name = dfObj[column_name].tolist()
    improper_name = list(set(improper_name))

    # Dictionaries will have key value pair as improper and proper name
    logs = {}
    changes = {}
    corrupt = {}

    scorers = [fuzz.token_set_ratio, fuzz.ratio]

    for query in improper_name:
        result = get_best_match(query, proper_name, thresh, data, scorers)
        if result:
            changes[query] = result
        elif query not in manual_changes:
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
