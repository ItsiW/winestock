import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

REFERER = "https://www.wine.com/list/wine/7155"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
)
COOKIE = "visitor_id=8aa22959-2413-4f6f-af94-98123a8261f8; selectedShippingState=CA; rr_rcs=eF5j4cotK8lM4TE30jXUNWQpTfawMDFMMzUxstQ1SDE01jUxN0vUNbdMswASZgYmBhaWyWlmiQBnaw0m; CSRF=AUODXnLa-Zrnvy0EPJKsoLGQlmFCej5fihlc; ldvisitor=96fb22a7-62b8-4f60-9778-37e58beba806; unrecognized_usergroup=3; hasSeenPromoModal=true; expandFilters=true; canMakePaymentsWithApplePay=false; utag_main=v_id:01814b57a0260009173fbab7aa0e05046002f00900dc4"

ALL_WINE_TYPES = ["all"]


def get_data_wine_dot_com(
    wine_type: str, page: int = 1, get_n_pages: bool = False
):
    assert wine_type in ALL_WINE_TYPES

    s = requests.Session()

    suffix = f"/{page}?sortBy=savings&pricemax=30"
    url = REFERER + suffix

    r = s.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Referer": REFERER,
            "Cookie": COOKIE,
        },
    )
    soup = BeautifulSoup(r.content, "html.parser")

    listings = soup.find_all(class_="prodItem")
    wines = []

    for listing in listings:
        try:
            title = listing.find(class_="prodItemInfo_name").text
            price = float(
                listing.find("meta", {"itemprop": "price"})["content"]
            )
            price_whole = int(
                listing.find(class_="productPrice_price-regWhole").text
            ) + (
                int(
                    listing.find(
                        class_="productPrice_price-regFractional"
                    ).text
                )
                / 100
                if len(
                    listing.find(
                        class_="productPrice_price-regFractional"
                    ).text
                )
                > 0
                else 0
            )
            url = (
                "https://www.wine.com"
                + listing.find(class_="prodItemInfo_link")["href"]
            )

            wines.append([title, price, price_whole, url])
        except AttributeError:
            assert (
                listing.find(class_="prodItemStock_soldOut").text[:12]
                == "Out of Stock"
            )

    df = pd.DataFrame(wines, columns=["title", "price", "price_whole", "url"])

    if get_n_pages:
        n_items = int(soup.find(class_="count").text.replace(",", ""))
        return _format_df_wine_dot_com(df), n_items // 25 + 1

    return _format_df_wine_dot_com(df)


def _format_df_wine_dot_com(data: pd.DataFrame):

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
