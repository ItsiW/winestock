import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

NOEVALLEY_BASE_URL = "https://www.noevalleywineandspirits.com"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
)

ALL_WINE_TYPES = ["all"]


def get_data_noevalley(
    wine_type: str, page: int = 1, get_n_pages: bool = False
):

    s = requests.Session()
    url = f"{NOEVALLEY_BASE_URL}/wine/page{page}.html?limit=100&sort=lowest"
    r = s.get(url, headers={"User-Agent": USER_AGENT, "Referer": url})

    soup = BeautifulSoup(r.content, "html.parser")
    listings = soup.find_all(class_="info")

    wines = []
    for item in listings:
        name = item.find(class_="title").text.strip()
        link = item.find_all("a")[0]["href"]
        price = float(item.find(class_="left").text.strip()[1:])

        wines.append([name, price, link])

    df = pd.DataFrame(wines, columns=["title", "price", "url"])

    if get_n_pages:
        try:
            n_pages = int(
                soup.find(class_="pager row")
                .find(class_="left")
                .text.split(" ")[-1]
            )
        except AttributeError:
            n_pages = 0

        return _format_noevalley_df(df), n_pages

    return _format_noevalley_df(df)


def _format_noevalley_df(data: pd.DataFrame):

    remove_list = [
        "Vineyards",
        "Vineyard",
        "Bodegas",
        "Bodega",
        "Cellars",
        "Cellar",
        "District",
    ]

    data["vintage"], data["search_name"] = zip(
        *data.title.apply(lambda x: _get_vintage(x))
    )
    for term in remove_list:
        data.loc[:, "search_name"] = data.search_name.replace(
            term, "", regex=True
        )

    # remove multiple spaces, trailing whitespace
    data.loc[:, "search_name"] = data.search_name.str.split().str.join(" ")
    return data


def _get_vintage(s: str):
    search = re.search(r"\b(19|20)\d{2}", s)
    if search:
        year = search.group()
        return int(year), s.replace(f" {year}", "")
    return None, s
