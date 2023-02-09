import re

import pandas as pd
import requests
from bs4 import BeautifulSoup

KL_BASE_URL = "https://www.klwines.com"

headers = {
    "Host": "www.klwines.com",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Cookie": """datadome=6Me6u~UF5DoXO-Kozv8Q9U9xJkciemr~8AEQL2q6yqf44y34emwEoiXYA-e9EvcZpTikCQcazu3EoCZlyV_PirJYEyzolmS1vPgDCkN~b_-rs3743gqTO-uY1lZHUrAT; ai_user=BkXlVtxFFvMiz98gzkGmRL|2022-11-15T08:42:06.107Z; TokenDTONew={"AccessToken":"eyJhbGciOiJSUzI1NiIsImtpZCI6IjE0MTEwMjA0RDRFNUVDNjRGQ0Y2NUU5MjU4MEJCQjEzQjBDQzc0RTUiLCJ0eXAiOiJKV1QiLCJ4NXQiOiJGQkVDQk5UbDdHVDg5bDZTV0F1N0U3RE1kT1UifQ.eyJuYmYiOjE2Njg1MDQxNzEsImV4cCI6MTY3MTA5NjE3MSwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS5rbHdpbmVzLmNvbSIsImF1ZCI6WyJodHRwczovL2lkZW50aXR5Lmtsd2luZXMuY29tL3Jlc291cmNlcyIsIktMV2luZXNBUEkiXSwiY2xpZW50X2lkIjoiS0xXaW5lc2FwcCIsInN1YiI6IjE1ODkyMzQ0IiwiYXV0aF90aW1lIjoxNjY4NTA0MTcxLCJpZHAiOiJsb2NhbCIsIklkIjoiMTU4OTIzNDQiLCJVc2VybmFtZSI6InNob3BAaXRzaXdlaW5zdG9jay5jb20iLCJSb2xlcyI6IiIsIlBlcm1pc3Npb25zIjoiIiwic2NvcGUiOlsiZW1haWwiLCJvcGVuaWQiLCJwcm9maWxlIiwia2x3aW5lc191c2VyIiwicm9sZXMiLCJvZmZsaW5lX2FjY2VzcyJdLCJhbXIiOlsicGFzc3dvcmQiXX0.KO3lrJjBJYBsIaZphw_va9s-HoVGx5TlEm6S8rmw_dBC5tSMsuM6LNnZgkhXT3BQLVKLuDE3xmEerZmrbK7QQHwg7DwnA_hziJvNfTkXOirZ3iWQ7rxeXAwdFca8B5Iri3JG6IyM4c6tsaSRBv0A5Ux-UM7YD8I0DLuCZBoxMdVV_QzHnX7ufibu7MJFH_MLgtSVrUgwxdnRgLWYEgsx6E3v819AIhNard5A__0nlQ5AlU6nS82CBwcEEqnu1tWZ6vL7UM1EnqA-qZJkRWx908B052dyzf9rMiB0kHCadQYViQtLhcg6H5hQZSoeF9G5YHtVFrr9KKajOJqeh85iTw","TokenType":"Bearer","ExpiresAtUtc":"2022-12-15T09:22:52.1003027Z","RefreshToken":"a9d4b339be42fad4046659d6010f731bcca7636c4dc882ed0da1f9dee36d409f"}; KLInsiderPricing=Y; KLS=PERSIST=TRUE&VERSION2=TRUE&ID=c8b87a1c975c457aa8cb0cacf7f3fd83; __RequestVerificationToken=g6Oz8IG2NdGRiZ8U1q6HwCtuWAg4OjI4VS51q56A6NxxAf6OGkNA1E53OqsHMEIpNHEX7M63jXKvkOReGNpZigG_vtuthTNYt5uXRLniCrU1; ARRAffinity=e2b06b808ea319177022f4c0f9d73529572bd2dadd343f2ccbb90a090135dd87; ARRAffinitySameSite=e2b06b808ea319177022f4c0f9d73529572bd2dadd343f2ccbb90a090135dd87; ASP.NET_SessionId=abuyffhwbad10ukuqqw1ipla; __cf_bm=5Jo0f3NFiwFEw4iK5SFhRD9vEhmR_5m0jDW_btFA724-1668840479-0-AepFfyI2U9YK98T30bB2/+Ni5rQNC5CjvKwgrS+hNhGzjWyMb4I7C7wUZmXG9Sq419JaII8w6UYpSpvKIxdMFtU=; ai_session=Ah3KxlycLG7tEQtt/3+U2A|1668839527027|1668840611746""".replace(
        "…", "..."
    ),
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "TE": "trailers",
}

ALL_WINE_TYPES = ["all"]


def get_data_kl(wine_type: str, page: int = 1, get_n_pages: bool = False):

    s = requests.Session()

    url = f"{KL_BASE_URL}/Products?&filters=sv2_30$eq$(227)$True$w$or,30$eq$(230)$True$$.or,30$eq$(225)$True$$.or,30$eq$(229)$True$$.or,30$eq$(226)$True$$.or,30$eq$(228)$True$$!10$ge$0$True$ListPrice$and,10$le$40$True$ListPriceTo$&limit=500&offset={str((page-1)*500)}&orderBy=60%20asc,10%20asc&searchText="

    r = s.get(
        url,
        headers=headers,
    )
    soup = BeautifulSoup(r.content, "html.parser")
    listings = soup.find_all(class_="tf-product clearfix")

    wines = []
    for item in listings:
        if "bid" in str(item).lower():
            continue
        descriptor = item.find(class_="tf-button")["onclick"]

        price = float(re.findall(r'"productPrice":(\d+\.\d+)', descriptor)[0])
        link = (
            f"{KL_BASE_URL}/p/i?i="
            + re.findall(r'"productId":"(\d+)"', descriptor)[0]
        )
        name = item.find("a").text.strip()

        wines.append([name, price, link])

    df = pd.DataFrame(wines, columns=["title", "price", "url"])

    if get_n_pages:
        try:
            n_pages = (
                int(
                    re.findall(
                        r"\d+",
                        soup.find(
                            class_="prod-feature-block result-count clearfix"
                        )
                        .find("h2")
                        .text,
                    )[0]
                )
                // 500
                + 1
            )
        except AttributeError:
            n_pages = 0

        return _format_df_kl(df), n_pages

    return _format_df_kl(df)


def _format_df_kl(data: pd.DataFrame):

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
        return int(year), s.replace(f"{year}", "").strip()
    return None, s
