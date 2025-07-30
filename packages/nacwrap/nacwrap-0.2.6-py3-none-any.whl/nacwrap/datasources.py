"""
Also called data lookups in the Nintex interface.
"""

import os

import requests

from nacwrap._auth import Decorators
from nacwrap._helpers import _basic_retry


@_basic_retry
@Decorators.refresh_token
def get_datasources() -> dict:
    """
    Get all data sources
    """
    if "NINTEX_BASE_URL" not in os.environ:
        raise Exception("NINTEX_BASE_URL not set")
    try:
        response = requests.get(
            os.environ["NINTEX_BASE_URL"] + "/workflows/v1/datasources",
            headers={
                "Authorization": f"Bearer {os.environ['NTX_BEARER_TOKEN']}",
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error getting data sources: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error getting data sources: {e}")

    return response.json().get("datasources", [])


@_basic_retry
@Decorators.refresh_token
def get_datasource_connectors() -> dict:
    """
    Get a list of connectors compatible with the xtensions data lookups
    """
    if "NINTEX_BASE_URL" not in os.environ:
        raise Exception("NINTEX_BASE_URL not set")
    try:
        response = requests.get(
            os.environ["NINTEX_BASE_URL"] + "/workflows/v1/datasources/contracts",
            headers={
                "Authorization": f"Bearer {os.environ['NTX_BEARER_TOKEN']}",
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error getting data source connectors: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error getting data source connectors: {e}")

    return response.json().get("contracts", [])
