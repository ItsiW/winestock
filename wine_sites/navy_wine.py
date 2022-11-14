import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

NAVYWINE_BASE_URL = "https://www.navywine.com"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
)

ALL_WINE_TYPES = ["red", "rose", "white", "orange", "sparkling"]


def get_data_navy_wine(
    wine_type: str, page: int = 1, get_n_pages: bool = False
):

    assert wine_type in ALL_WINE_TYPES

    s = requests.Session()
    url = f"{NAVYWINE_BASE_URL}/wine/{wine_type}/page{page}.html"
    r = s.get(url, headers={"User-Agent": USER_AGENT, "Referer": url})

    soup = BeautifulSoup(r.content, "html.parser")
    listings = soup.find_all(class_="product col-xs-6 col-sm-3 col-md-3")

    wines = []
    for item in listings:
        name = item.find(class_="text").text.strip()
        link = item.find_all("a")[1]["href"]
        price = float(item.find(class_="left").text.strip()[1:])

        wines.append([name, price, link])

    df = pd.DataFrame(wines, columns=["title", "price", "url"])

    if get_n_pages:
        try:
            n_pages = int(
                soup.find(class_="pager row")
                .find(class_="left")
                .text.split()[-1]
            )
        except AttributeError:
            n_pages = 1

        return _format_df_navy_wines(df), n_pages

    return _format_df_navy_wines(df)


def _format_df_navy_wines(data: pd.DataFrame):

    remove_list = [
        "Vineyards",
        "Vineyard",
        "Bodegas",
        "Bodega",
        "Cellars",
        "Cellar",
        "District",
    ]

    data["search_name"] = data.title.apply(lambda x: _remove_brackets(x))
    data["vintage"], data["search_name"] = zip(
        *data.search_name.apply(lambda x: _get_vintage(x))
    )

    for term in remove_list:
        data.loc[:, "search_name"] = data.search_name.replace(
            term, "", regex=True
        )

    # remove multiple spaces, trailing whitespace
    data.loc[:, "search_name"] = data.search_name.str.split().str.join(" ")

    return data


def _remove_brackets(s: str):
    if " (" in s:
        return s.replace(re.findall(r" \(.*\)", s)[0], "")
    return s


def _get_vintage(s: str):
    search = re.search(r"\b(19|20)\d{2}", s)
    if search:
        year = search.group()
        return int(year), s.replace(f" {year}", "")
    return None, s
