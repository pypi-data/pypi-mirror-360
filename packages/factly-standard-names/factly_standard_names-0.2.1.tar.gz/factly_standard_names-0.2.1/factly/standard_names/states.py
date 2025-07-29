import json

from fuzzywuzzy import fuzz, process

from .utils import get_std_abbreviations, get_std_names


def getIndexes(dfObj, value):
    """Get index positions of value in dataframe i.e. dfObj."""
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col]].index)
        for row in rows:
            listOfPos.append((row, col))
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos


def state_std_names(
    dfObj, column_name, thresh=70, manual_changes={}, identifier="None"
):
    """
    find all improper state names from a given dataframe
    and replaces it with standard names proved.
    dfObj : DataFrame object on which states name should be standardize
    column_name : name of column which has entries as state name
    manual_changes = Dict , default : null dict , changes in names done manually.
    """

    proper_name = get_std_names(filter="state")  # gets the list of standard state names
    proper_name = [name.strip() for name in proper_name]

    improper_name = dfObj[column_name].tolist()
    improper_name = list(set(improper_name))

    # Dictionaries will have key value pair as improper and proper name
    logs = {}
    changes = {}
    corrupt = {}
    # will probably create filters for ratio
    for query in improper_name:
        match = process.extract(query.strip(), proper_name, scorer=fuzz.token_set_ratio)
        if match[0][1] >= thresh and match[0][1] >= match[1][1] + 2:
            changes[query] = match[0][0]
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


def state_abbr_std_names(dfObj, column_name, manual_changes={}, identifier="None"):

    """
    find all state names from respective state abbreviation from a given dataframe
    and replaces it with standard names proved.
    dfObj : DataFrame object on which states abbreviation should be standardize
    column_name : name of column which has entries as state abbreviation
    manual_changes = Dict , default : null dict , changes in names done manually.
    """

    df_map = get_std_abbreviations(
        filter=["state", "state_abbreviation"]
    )  # gets the dataframe of state and abbreviation
    proper_names = df_map[df_map.columns[1]].to_list()

    improper_names = dfObj[column_name].unique()

    # Dictionaries will have key value pair as improper and proper name
    logs = {}
    changes = {}
    corrupt = {}

    for query in list(improper_names):
        if query in list(proper_names):
            changes[query] = df_map.loc[
                (df_map[df_map.columns[1]] == query), "state"
            ].values[0]
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
