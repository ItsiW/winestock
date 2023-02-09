from wine_sites.berkeley_bowl import ALL_WINE_TYPES as berkeley_bowl_types
from wine_sites.berkeley_bowl import get_data_berkeley_bowl
from wine_sites.best_buy import ALL_WINE_TYPES as best_buy_types
from wine_sites.best_buy import get_data_best_buy
from wine_sites.kl import ALL_WINE_TYPES as kl_types
from wine_sites.kl import get_data_kl
from wine_sites.navy_wine import ALL_WINE_TYPES as navy_wine_types
from wine_sites.navy_wine import get_data_navy_wine
from wine_sites.noevalley import ALL_WINE_TYPES as noevalley_types
from wine_sites.noevalley import get_data_noevalley
from wine_sites.wine_dot_com import ALL_WINE_TYPES as wine_dot_com_types
from wine_sites.wine_dot_com import get_data_wine_dot_com

SITES = [
    "Berkeley Bowl",
    "wine.com",
    "Best Buy",
    "Navy Wine",
    "Noe Valley",
    "K L",
]


def get_site_fn(site: str):
    """
    fetches the right function for getting a page of data for a wine category
    """
    assert site in SITES

    if site == "Berkeley Bowl":
        return get_data_berkeley_bowl

    if site == "wine.com":
        return get_data_wine_dot_com

    if site == "Best Buy":
        return get_data_best_buy

    if site == "Navy Wine":
        return get_data_navy_wine

    if site == "Noe Valley":
        return get_data_noevalley

    if site == "K L":
        return get_data_kl


def get_all_types(site: str):
    """
    returns all wine types for a given site
    """
    assert site in SITES

    if site == "Berkeley Bowl":
        return berkeley_bowl_types

    if site == "wine.com":
        return wine_dot_com_types

    if site == "Best Buy":
        return best_buy_types

    if site == "Navy Wine":
        return navy_wine_types

    if site == "Noe Valley":
        return noevalley_types

    if site == "K L":
        return kl_types
