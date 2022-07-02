import json
import re

import pandas as pd
import requests

BB_BASE_URL = "https://shop.heinzcatering.berkeleybowl.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
BB_SEARCH_PATTERN = 'var ProductCard.*props = (.*),"onAddToCart.*;'

ALL_WINE_TYPES = [
    "popular_wine",
    "us_reds",
    "rose",
    "us_whites",
    "sparkling_wine",
    "spanish_portuguese_wine",
    "italian_wine",
    "french_wine",
    "german_austrian_wine",
    "southern_hemisphere_wine",
    "natural_wine",
    "dessert_wine",
]


def get_data_berkeley_bowl(
    wine_type: str, page: int = 1, get_n_pages: bool = False
):

    assert wine_type in ALL_WINE_TYPES

    s = requests.Session()
    referer = BB_BASE_URL + "category/beer_wine_" + wine_type
    suffix = f"?_pjax=%23categories-pjax-container&page={page}&per-page=24"
    url = referer + suffix
    r = s.get(url, headers={"User-Agent": USER_AGENT, "Referer": referer})

    wines = []
    for m in re.finditer(BB_SEARCH_PATTERN, r.text):
        wines.append(json.loads(m.group(1) + "}"))
    data = pd.DataFrame(wines)

    if get_n_pages:
        try:
            return _format_df_berkeley_bowl(data), int(
                max(re.findall(r"page=([0-9]*)&amp;per-page=24", r.text))
            )
        except ValueError:
            return _format_df_berkeley_bowl(data), 1

    return _format_df_berkeley_bowl(data)


def _format_df_berkeley_bowl(data: pd.DataFrame):

    remove_list = [
        r"20\d\d",
        r"750.*",
        "Vineyards",
        "Vineyard",
        "Bodegas",
        "Bodega",
        "Cellars",
        "Cellar",
    ]

    data.loc[:, "price"] = data.priceFull.str[2:].astype(float)
    data.loc[:, "url"] = BB_BASE_URL + "product/" + data.upc.astype(str)
    data.loc[:, "vintage"] = None
    data = data.loc[:, ["title", "url", "price", "vintage"]]

    data.loc[:, "search_name"] = data.title
    for term in remove_list:
        data.loc[:, "search_name"] = data.search_name.replace(
            term, "", regex=True
        )
    # remove multiple spaces, trailing whitespace
    data.loc[:, "search_name"] = data.search_name.str.split().str.join(" ")

    data.loc[
        data.search_name.str.lower().str.endswith("wine"), "search_name"
    ] = data.loc[
        data.search_name.str.lower().str.endswith("wine")
    ].search_name.str[
        :-5
    ]
    data.loc[
        data.search_name.str.lower().str.startswith("wine "), "search_name"
    ] = data.loc[
        data.search_name.str.lower().str.startswith("wine ")
    ].search_name.str[
        5:
    ]
    return data
