import datetime
import os
from pathlib import Path

import pandas as pd
from IPython.display import HTML
from unidecode import unidecode

from wine_sites.wine_site_functions import SITES


def flag_errors(df):
    """
    Adds a column "error_flag" to a pandas dataframe
    A row is flagged if the name in vivino and the search name do not match

    Arguments
    df: a pandas dataframe

    Returns
    copy_df: a copy of the original dataframe with the added error_flag column
    """
    copy_df = df.copy(deep=True)
    copy_df["error_flag"] = copy_df.apply(
        lambda row: _flag_errors(row), axis=1
    )
    return copy_df


def _flag_errors(row):
    """
    Returns true if the words of vivino_name are not a subset of search_name
    or vice versa
    """
    if type(row.vivino_name) is not str or type(row.search_name) is not str:
        return True

    remove_list = [
        "California",
        "(",
        ")",
        "Wines",
        "Wine",
        "North Coast",
        "Mendoza Argentina",
        "Cellars",
        "Cellar",
        "Vineyards",
        "Vineyard",
    ]
    replace_list = {
        (" Co.", " Co"),
        (" De ", " "),
        (" de ", " "),
        ("&", "and"),
        ('"', ""),
        ("'", ""),
        ("-", " - "),
    }

    search_name = unidecode(row.search_name).rstrip()
    vivino_name = unidecode(row.vivino_name).rstrip()

    for term in remove_list:
        search_name = search_name.replace(term, "")
        vivino_name = vivino_name.replace(term, "")

    for terms in replace_list:
        search_name = search_name.replace(terms[0], terms[1])
        vivino_name = vivino_name.replace(terms[0], terms[1])

    search_name = " ".join(search_name.split())
    vivino_name = " ".join(vivino_name.split())

    search_name = search_name.lower().split(" ")
    vivino_name = vivino_name.lower().split(" ")

    search_name = [
        word[:-1] if word[-1] == "s" else word for word in search_name
    ]
    vivino_name = [
        word[:-1] if word[-1] == "s" else word for word in vivino_name
    ]

    return not (
        set(vivino_name).issubset(set(search_name))
        or set(search_name).issubset(set(vivino_name))
    )


def view_links(df):
    """
    Adds columns for links for the store and vivino URLs and renders them
    """
    view_df = df.copy()
    view_df["vivino_clickable"] = view_df.vivino_link.apply(
        lambda x: f"<a href='{x}'>Vivino link</a>"
    )
    view_df["store_clickable"] = view_df.url.apply(
        lambda x: f"<a href='{x}'>Store link</a>"
    )
    return HTML(
        view_df.drop(["url", "vivino_link"], axis=1).to_html(escape=False)
    )


def get_latest_scrape(site: str):
    """
    Finds the most recent csv for a website and returns a pandas dataframe
    """
    assert site in SITES

    latest_file = sorted(
        [
            file
            for file in os.listdir("results")
            if site.lower().replace(" ", "_") in file
        ]
    )[-1]

    date, time = latest_file.replace(".csv", "").split("_")[2:4]
    dt = datetime.datetime(
        int(date[:4]),
        int(date[4:6]),
        int(date[6:8]),
        int(time[:2]),
        int(time[2:4]),
        int(time[4:6]),
    )
    print(f"Last {site} dataframe: {dt}\nfilename: {latest_file}")

    df = pd.read_csv(Path("results") / Path(latest_file))
    return df.drop(df.columns[0], axis=1) if df.columns[0] != "title" else df
