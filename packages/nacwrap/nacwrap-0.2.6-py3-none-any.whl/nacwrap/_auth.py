import os
from datetime import datetime

import requests


class Decorators:
    """
    Decorators class
    """

    @staticmethod
    def refresh_token(decorated):
        """
        Decorator to refresh the access token if it has expired or generate
        a new one if it does not exist.
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper function
            """
            if "NTX_BEARER_TOKEN_EXPIRES_AT" not in os.environ:
                expires_at = "01/01/1901 00:00:00"
            else:
                expires_at = os.environ["NTX_BEARER_TOKEN_EXPIRES_AT"]
            if (
                "NTX_BEARER_TOKEN" not in os.environ
                or datetime.strptime(expires_at, "%m/%d/%Y %H:%M:%S") < datetime.now()
            ):
                Decorators.get_token()
            return decorated(*args, **kwargs)

        wrapper.__name__ = decorated.__name__
        return wrapper

    @staticmethod
    def get_token():
        """
        Get Nintex bearer token
        """
        if "NINTEX_BASE_URL" not in os.environ:
            raise Exception("NINTEX_BASE_URL not set in environment")
        if "NINTEX_CLIENT_ID" not in os.environ:
            raise Exception("NINTEX_CLIENT_ID not set in environment")
        if "NINTEX_CLIENT_SECRET" not in os.environ:
            raise Exception("NINTEX_CLIENT_SECRET not set in environment")
        if "NINTEX_GRANT_TYPE" not in os.environ:
            raise Exception("NINTEX_GRANT_TYPE not set in environment")

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(
            os.environ["NINTEX_BASE_URL"] + "/authentication/v1/token",
            headers=headers,
            data={
                "client_id": os.environ["NINTEX_CLIENT_ID"],
                "client_secret": os.environ["NINTEX_CLIENT_SECRET"],
                "grant_type": os.environ["NINTEX_GRANT_TYPE"],
            },
            timeout=30,
        )
        try:
            os.environ["NTX_BEARER_TOKEN"] = response.json()["access_token"]
        except Exception as e:
            raise Exception(f"Error, could not set OS env bearer token: {e}")
        try:
            os.environ["NTX_EXPIRES_AT"] = response.json()["expires_at"]
        except Exception as e:
            raise Exception(f"Error, could not set os env expires at: {e}")
