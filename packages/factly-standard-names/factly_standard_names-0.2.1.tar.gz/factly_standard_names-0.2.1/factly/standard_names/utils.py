import pandas as pd

from . import settings

std_names_url = f"https://docs.google.com/spreadsheets/d/{settings.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={settings.STANDARD_NAMES_SHEET_NAME}"
std_abbr_url = f"https://docs.google.com/spreadsheets/d/{settings.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={settings.ABBREVIATIONS_SHEET_NAME}"
std_country_url = f"https://docs.google.com/spreadsheets/d/{settings.SHEET_ID}/gviz/tq?tqx=out:csv&sheet={settings.COUNTRY_SHEET_NAME}"


def get_std_names(filter: str):
    """
    Get the standard names from the google sheet.
    :param filter: str
    :return: list of standard names
    """
    data = pd.read_csv(std_names_url)
    return data[filter].dropna().tolist()


def get_std_abbreviations(filter: list):
    """
    Get the standard abbreviations from the google sheet.
    :param filter: list of column names
    :return: DataFrame
    """
    data = pd.read_csv(std_abbr_url)
    return data[filter].dropna()


def get_country_data():
    """
    Get the country data from the google sheet.
    :return: DataFrame
    """
    data = pd.read_csv(std_country_url)[["country_name", "standard_country_name"]]
    return data.dropna(how="all")
