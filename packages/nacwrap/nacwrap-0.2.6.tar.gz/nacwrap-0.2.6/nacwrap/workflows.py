"""
This module contains functions to interact with workflows
"""

import json
import os
from datetime import datetime
from typing import Literal, Optional, Union

import requests

from nacwrap._auth import Decorators
from nacwrap._helpers import _fetch_page, _post
from nacwrap.data_model import *
from nacwrap.exceptions import *


# TODO List workflows
@Decorators.refresh_token
def workflows_list(limit: int = 1000) -> dict:
    """Get Nintex Workflow information.

    Args:
        limit (int, optional): Max number of workflows to return. Defaults to 1000.

    Raises:
        WorkflowApiError: Generic error when API call fails.

    Returns:
        list[dict]: _description_
    """

    base_url = (
        os.environ["NINTEX_BASE_URL"] + f"/workflows/v1/designs/published?limit={limit}"
    )
    results = []
    url = base_url

    while url:

        try:
            response = _fetch_page(
                url,
                headers={
                    "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise WorkflowApiError(
                f"Error, could not get workflow data: {e.response.status_code} - {e.response.content}"
            )
        except requests.exceptions.RequestException as e:
            raise WorkflowApiError(f"Error, could not get workflow data: {e}")

        data = response.json()
        results += data["workflows"]
        url = data.get("nextLink")

    return results


def workflows_list_pd(limit: int = 1000) -> NintexWorkflows:
    """Get Nintex Workflow information.
    Returns data as a pydantic data model.

    Returns:
        NintexWorkflows: Pydantic data model of API response.
    """

    workflows = workflows_list(limit=limit)
    return NintexWorkflows(workflows=workflows)


# TODO List Workflow permissions

# TODO Update workflow permissions

# TODO Get a workflow design

# TODO Delete a workflow

# TODO Deactivate a workflow

# TODO Activate a workflow

# TODO Add tags to a workflow

# TODO Export a draft workflow

# TODO Export a published workflow

# TODO Import a workflow
