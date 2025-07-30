import os

import requests

from nacwrap._auth import Decorators
from nacwrap._helpers import _basic_retry


@_basic_retry
@Decorators.refresh_token
def get_connections() -> list[dict]:
    """
    Get all connections
    """
    if "NINTEX_BASE_URL" not in os.environ:
        raise Exception("NINTEX_BASE_URL not set")
    try:
        response = requests.get(
            os.environ["NINTEX_BASE_URL"] + "/workflows/v1/connections",
            headers={
                "Authorization": f"Bearer {os.environ['NTX_BEARER_TOKEN']}",
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error getting connections: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        raise
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error getting connections: {e}")

    return response.json().get("connections", [])
