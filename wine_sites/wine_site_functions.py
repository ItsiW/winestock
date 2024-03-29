from wine_sites.berkeley_bowl import ALL_WINE_TYPES as berkeley_bowl_types
from wine_sites.berkeley_bowl import get_data_berkeley_bowl
from wine_sites.wine_dot_com import ALL_WINE_TYPES as wine_dot_com_types
from wine_sites.wine_dot_com import get_data_wine_dot_com

SITES = ["Berkeley Bowl", "wine.com"]


def get_site_fn(site: str):
    """
    fetches the right function for getting a page of data for a wine category
    """
    assert site in SITES

    if site == "Berkeley Bowl":
        return get_data_berkeley_bowl

    if site == "wine.com":
        return get_data_wine_dot_com


def get_all_types(site: str):
    """
    returns all wine types for a given site
    """
    assert site in SITES

    if site == "Berkeley Bowl":
        return berkeley_bowl_types

    if site == "wine.com":
        return wine_dot_com_types
