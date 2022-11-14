import pandas as pd
import requests
from bs4 import BeautifulSoup

BESTBUY_BASE_URL = "https://www.bestbuywinewarehouse.com"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
)

ALL_WINE_TYPES = [
    "red-wine",
    "white-wine",
    "wine",
]


def get_data_best_buy(
    wine_type: str, page: int = 1, get_n_pages: bool = False
):
    assert wine_type in ALL_WINE_TYPES

    s = requests.Session()
    url = f"{BESTBUY_BASE_URL}/collections/all/{wine_type}?page={page}"
    r = s.get(url, headers={"User-Agent": USER_AGENT, "Referer": url})

    soup = BeautifulSoup(r.content, "html.parser")

    name_listings = soup.find_all(
        class_="h4 grid-view-item__title product-card__title"
    )
    price_listings = soup.find_all(class_="price-item price-item--regular")
    link_listings = soup.find_all(
        class_="grid-view-item__link grid-view-item__image-container full-width-link"
    )

    wines = []
    for i in range(len(name_listings)):
        price = price_listings[i].text.strip()[1:]
        wines.append(
            [
                name_listings[i].text.strip(),
                float(price) if is_float(price) else None,
                BESTBUY_BASE_URL + link_listings[i].attrs["href"],
            ]
        )
    df = pd.DataFrame(wines, columns=["title", "price", "url"])

    if get_n_pages:
        return _format_df_best_buy(df), float(
            soup.find(class_="pagination__text").text.strip().split()[-1]
        )

    return _format_df_best_buy(df)


def is_float(x: str):
    try:
        float(x)
        return True
    except ValueError:
        return False


def _format_df_best_buy(data: pd.DataFrame):

    remove_list = [
        "Vineyards",
        "Vineyard",
        "Bodegas",
        "Bodega",
        "Cellars",
        "Cellar",
        "District",
    ]

    data["search_name"] = data["title"].copy()
    data["vintage"] = None

    for term in remove_list:
        data.loc[:, "search_name"] = data.search_name.replace(
            term, "", regex=True
        )

    # remove multiple spaces, trailing whitespace
    data.loc[:, "search_name"] = data.search_name.str.split().str.join(" ")

    return data
