import datetime
import json
import logging
import re
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry
from tqdm.auto import tqdm

from wine_sites.wine_site_functions import SITES, get_site_fn

ONE_MINUTE = 60
CALLS_PER_MINUTE = 9

VIVINO_SEARCH_URL_BASE = "https://www.vivino.com/search/wines?q="
VIVINO_REFERER = "https://www.vivino.com/AU/en/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
VIVINO_INFO_PATTERN = '{"vintage":{"id.*;\n'


def search_site(site: str, categories: List[str]):
    """
    Searches a website for a set list of categories.
    A pandas dataframe is made with all the wines found
    Each wine is searched in vivino for its score and other details

    The function returns the final dataframe, and writes it as a csv
    """
    page_data_fn = get_site_fn(site)
    wine_df = pd.DataFrame()

    logging.warning(
        f"Vivino calls rate limited to {CALLS_PER_MINUTE} per minute"
    )

    for wine_type in categories:
        df = pd.DataFrame()

        page = 1
        # loop through pages
        while True:
            # for the first page, get the total number of pages
            if page == 1:
                try:
                    data, n_pages = page_data_fn(
                        wine_type, page=1, get_n_pages=True
                    )
                    logging.warning(f"{n_pages} pages for {wine_type}")
                except Exception:
                    logging.warning(
                        f"Error searching for {wine_type}", exc_info=True
                    )
                    break
            else:
                try:
                    data = page_data_fn(
                        wine_type, page=page, get_n_pages=False
                    )
                except Exception:
                    logging.warning(
                        f"Could not retrieve page {page} for type {wine_type}",
                        exc_info=True,
                    )
                    page += 1
                    if page > n_pages:
                        break
                    continue

            # search each wine in vivino
            tqdm.pandas(desc=f"type: {wine_type}, page: {page}/{n_pages}")
            (
                data["vivino_score"],
                data["num_reviews"],
                data["vivino_name"],
                data["vivino_link"],
            ) = zip(
                *data.search_name.progress_apply(lambda x: search_vivino(x))
            )
            df = pd.concat([df, data]).reset_index(drop=True)

            page += 1

            df.to_csv("results/most_recent.csv")

            if page > n_pages:
                break

        if len(df) > 0:
            df["wine_type"] = wine_type
            wine_df = pd.concat([wine_df, df]).reset_index(drop=True)

    filename = (
        site.lower().replace(" ", "_")
        + "_"
        + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".csv"
    )

    location = Path("results") / Path(filename)
    wine_df.to_csv(location)
    logging.warning(f"Wine dataframe saved to {location}")

    return wine_df


def search_vivino(name: str):
    """
    Searches vivino.com using the given name string and processes the first result

    Returns the score out of 5, the number of ratings,
    the name of the wine on vivino, and the link to its page on vivino
    """
    try:
        url = (VIVINO_SEARCH_URL_BASE + name).replace(" ", "+")
        url = url.replace("&", "%26")

        page = _vivino_request_page(url)
        soup = BeautifulSoup(page.content, "html.parser")
        listing = soup.find(class_="card card-lg")

        link = "https://www.vivino.com" + listing.find(
            class_="link-color-alt-grey"
        ).get("href")
        v_name = listing.find(class_="link-color-alt-grey").text.replace(
            "\n", ""
        )

        try:
            score = float(
                listing.find(
                    class_="text-inline-block light average__number"
                ).text.replace("\n", "")
            )
        except AttributeError:
            logging.info(f"Can not find score for {name}", exc_info=True)
            score = None
        try:
            n_scores = int(
                listing.find(class_="text-micro")
                .text.replace("\n", "")
                .replace(" ratings", "")
            )
        except AttributeError:
            logging.info(f"Can not find n_scores for {name}", exc_info=True)
            n_scores = None

        return score, n_scores, v_name, link

    except Exception:
        logging.warning(f"Error for {name}", exc_info=True)
        return None, None, None, None


@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=ONE_MINUTE)
def _vivino_request_page(url: str):
    """
    rate limited function to request url
    """
    s = requests.Session()
    return s.get(
        url, headers={"User-Agent": USER_AGENT, "Referer": VIVINO_REFERER}
    )


def add_vivino_info(df: pd.DataFrame, site: str):
    """
    Add info from each vivino link to the dataframe and save to csv
    """

    assert site in SITES

    tqdm.pandas(desc="adding Vivino page data")
    (
        df["country"],
        df["region"],
        df["winery_region"],
        df["vintage_score"],
        df["vintage_num_reviews"],
        df["style"],
        df["alcohol_perc"],
        df["vivino_price"],
    ) = zip(*df.progress_apply(lambda row: _add_vivino_info(row), axis=1))

    filename = (
        site.lower().replace(" ", "_")
        + "_"
        + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + "_vivino_info"
        + ".csv"
    )

    location = Path("results") / Path(filename)
    df.to_csv(location)
    logging.warning(f"Wine dataframe with Vivino info saved to {location}")

    return df


def _add_vivino_info(row):

    try:
        r = _vivino_request_page(row.vivino_link)

        dic = json.loads(re.search(VIVINO_INFO_PATTERN, r.text).group()[:-2])

        try:
            country = dic["vintage"]["wine"]["region"]["country"]["name"]
        except TypeError:
            country = dic["wine"]["winery"]["region"]["country"]["name"]

        try:
            region = dic["vintage"]["wine"]["region"]["name"]
        except TypeError:
            region = None

        try:
            winery_region = dic["wine"]["winery"]["region"]["name"]
        except KeyError:
            winery_region = None

        if row.vintage:
            try:
                entry = next(
                    item
                    for item in dic["vintage"]["wine"]["vintages"]
                    if item["year"] == row.vintage
                )
                vintage_score = entry["statistics"]["ratings_average"]
                vintage_num_reviews = entry["statistics"]["ratings_count"]
            except StopIteration:
                vintage_score = None
                vintage_num_reviews = None
        else:
            vintage_score = None
            vintage_num_reviews = None

        try:
            style = dic["vintage"]["wine"]["style"]["varietal_name"]
        except TypeError:
            style = None

        alcohol_perc = dic["vintage"]["wine"]["alcohol"]
        if alcohol_perc == 0:
            alcohol_perc = None

        if len(dic["highlights"]) > 0:
            if row.vintage:
                try:
                    price = next(
                        year
                        for year in dic["highlights"]
                        if year["vintage_year"] == row.vintage
                    )["metadata"]["price"]["amount"]
                except (StopIteration, TypeError):
                    price = min(
                        [
                            year["metadata"]["price"]["amount"]
                            if year["metadata"]["price"]
                            else np.inf
                            for year in dic["highlights"]
                        ]
                    )
            else:
                price = min(
                    [
                        year["metadata"]["price"]["amount"]
                        if year["metadata"]["price"]
                        else np.inf
                        for year in dic["highlights"]
                    ]
                )

        else:
            price = None

        if price == np.inf:
            price = None

        return (
            country,
            region,
            winery_region,
            vintage_score,
            vintage_num_reviews,
            style,
            alcohol_perc,
            price,
        )

    except Exception:
        logging.warning(f"Error for {row.title}", exc_info=True)
        return None, None, None, None, None, None, None, None
