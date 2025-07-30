import json
import os
from datetime import datetime
from typing import List, Literal, Optional, Union

import requests

from nacwrap._auth import Decorators
from nacwrap._helpers import _basic_retry, _fetch_page, _post
from nacwrap.data_model import (
    InstanceActions,
    InstanceStartData,
    NintexInstance,
    ResolveType,
)


@_basic_retry
@Decorators.refresh_token
def create_instance(workflow_id: str, start_data: Optional[dict] = None) -> dict:
    """
    Creates a Nintex workflow instance for a given workflow.
    If successful, returns response which should be a dict containing
    instance ID that was created.

    :param workflow_id: ID of the component workflow to create an instance for
    :param start_data: dictionary of start data, if the component workflow has any
    """
    if "NINTEX_BASE_URL" not in os.environ:
        raise Exception("NINTEX_BASE_URL not set in environment")
    if start_data is None:
        start_data = {}
    try:
        data = json.dumps({"startData": start_data})
        response = requests.post(
            os.environ["NINTEX_BASE_URL"]
            + "/workflows/v1/designs/"
            + workflow_id
            + "/instances",
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
            data=data,
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error creating instance for {start_data}: {e.response.status_code} - {e.response.content}"
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error creating instance for {start_data}: {e}")

    return response.json()


@_basic_retry
@Decorators.refresh_token
def instance_get(instanceId: str) -> dict:
    """
    Calls Nintex's 'Get a Workflow Instance' API endpoint.
    Returns data as python dictionary.

    :param instanceId: Unuiqe ID of workflow instance to return data for.
    """
    base_url = os.environ["NINTEX_BASE_URL"] + f"/workflows/v2/instances/{instanceId}"
    params = {"instanceId": instanceId}

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    results = {}
    url = base_url
    first_request = True

    while url:
        # If this is subsequent requests, don't need to pass params
        # will be provided in the skip URL
        if first_request:
            first_request = False
        else:
            params = None

        try:
            response = _fetch_page(
                url,
                headers={
                    "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                    "Content-Type": "application/json",
                },
                params=params,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            raise Exception(
                f"Error, could not get instance data: {e.response.status_code} - {e.response.content}"
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            raise
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error, could not get instance data: {e}")

        data = response.json()
        results = {**results, **data}
        url = data.get("nextLink")

    return results


def instance_get_pd(instanceId: str) -> InstanceActions:
    """
    Calls Nintex's 'Get a Workflow Instance' API endpoint.
    Returns data as a pydantic data model.

    :param instanceId: Unuiqe ID of workflow instance to return data for.
    """
    instance = instance_get(instanceId=instanceId)
    return InstanceActions(**instance)


def get_instance_data(
    workflow_name: Optional[str] = None,
    status: Optional[str] = None,
    order_by: Union[Literal["ASC", "DESC"], None] = None,
    from_datetime: Optional[datetime] = None,
    to_datetime: Optional[datetime] = None,
    page_size: Optional[int] = 100,
) -> list[dict]:
    """
    This method is deprecated and list_instances() should be called directly instead.
    Wrapper method for calling list_instances().

    Get Nintex instance data Follows nextLink until no more pages.
    Function goes through all instance data in Nintex.

    Note: If from_datetime and to_datetime are not provided, the Nintex API
    defaults to returning the last 30 days. If you want everything, you need to
    explicitly use some sufficiently large time range.

    :param workflow_name: Name of the workflow to filter by
    :param status: Status of the workflow to filter by
    :param order_by: Order of the results
    :param from_datetime: Start date to filter by
    :param to_datetime: End date to filter by
    :param page_size: Number of results per page
    """

    return instances_list(
        workflow_name=workflow_name,
        status=status,
        order_by=order_by,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        page_size=page_size,
    )


@Decorators.refresh_token
def instances_list(
    workflow_name: Optional[str] = None,
    status: Optional[str] = None,
    order_by: Union[Literal["ASC", "DESC"], None] = None,
    from_datetime: Optional[datetime] = None,
    to_datetime: Optional[datetime] = None,
    page_size: Optional[int] = 100,
) -> list[dict]:
    """
    Get Nintex instance data Follows nextLink until no more pages.
    Function goes through all instance data in Nintex.

    Note: If from_datetime and to_datetime are not provided, the Nintex API
    defaults to returning the last 30 days. If you want everything, you need to
    explicitly use some sufficiently large time range.

    :param workflow_name: Name of the workflow to filter by
    :param status: Status of the workflow to filter by
    :param order_by: Order of the results
    :param from_datetime: Start date to filter by
    :param to_datetime: End date to filter by
    :param page_size: Number of results per page
    """
    if status is not None:
        status = status.value

    base_url = os.environ["NINTEX_BASE_URL"] + "/workflows/v2/instances"
    params = {
        "workflowName": workflow_name,
        "status": status,
        "order": order_by,
        "from": (
            from_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if from_datetime else None
        ),
        "to": to_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if to_datetime else None,
        "pageSize": page_size,
    }

    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    results = []
    url = base_url
    first_request = True

    while url:
        # If this is subsequent requests, don't need to pass params
        # will be provided in the skip URL
        if first_request:
            first_request = False
        else:
            params = None

        try:
            response = _fetch_page(
                url,
                headers={
                    "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                    "Content-Type": "application/json",
                },
                params=params,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(
                f"Error, could not get instance data: {e.response.status_code} - {e.response.content}"
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            raise
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error, could not get instance data: {e}")

        data = response.json()
        results += data["instances"]
        url = data.get("nextLink")

    return results


@Decorators.refresh_token
def instances_list_pd(
    workflow_name: Optional[str] = None,
    status: Optional[str] = None,
    order_by: Union[Literal["ASC", "DESC"], None] = None,
    from_datetime: Optional[datetime] = None,
    to_datetime: Optional[datetime] = None,
    page_size: Optional[int] = 100,
) -> List[NintexInstance]:
    """
    Get Nintex instance data Follows nextLink until no more pages.
    Returns a list of NintexInstance pydantic objects.

    :param workflow_name: Name of the workflow to filter by
    :param status: Status of the workflow to filter by
    :param order_by: Order of the results
    :param from_datetime: Start date to filter by
    :param to_datetime: End date to filter by
    :param page_size: Number of results per page
    """
    instance = instances_list(
        workflow_name=workflow_name,
        status=status,
        order_by=order_by,
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        page_size=page_size,
    )
    result: List[NintexInstance] = []
    for i in instance:
        result.append(NintexInstance(**i))

    return result


@Decorators.refresh_token
def instance_resolve(instance_id: str, resolveType: ResolveType, message: str):
    """
    Resolves a paused workflow instance.

    :param instance_id: ID of instance to resolve.
    :param resolveType: Specify how to resolve the paused instance: "1" to retry the failed action, "2" to fail the instance.
    :param message: Message to display on the workflow instance page
    """
    url = (
        os.environ["NINTEX_BASE_URL"] + f"/workflows/v1/instances/{instance_id}/resolve"
    )

    try:
        response = _post(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
            params={},
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error, user not found when resolving instance: {e.response.status_code} - {e.response.content}"
        )

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error, could not resolve instance: {e}")

    if response.status_code != 204:
        raise Exception(
            f"Error, invalid response code received when resolving instance: {e.response.status_code} - {e.response.content}"
        )


@Decorators.refresh_token
def instance_start_data(instance_id: str):
    """
    Returns start data from a specific workflow instance.

    :param instance_id: ID of instance to return start data for.
    """
    url = (
        os.environ["NINTEX_BASE_URL"]
        + f"/workflows/v2/instances/{instance_id}/startdata"
    )

    try:
        response = _fetch_page(
            url,
            headers={
                "Authorization": "Bearer " + os.environ["NTX_BEARER_TOKEN"],
                "Content-Type": "application/json",
            },
            params={},
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Error, instance not found when retrieving start data: {e.response.status_code} - {e.response.content}"
        )

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error, could not get instance start data: {e}")

    data = response.json()
    return data


def instance_start_data_pd(instance_id: str, pydantic_model: InstanceStartData):
    """
    Returns start data as a pydantic object for a specific workflow instance.

    :param instance_id: ID of instance to return start data for.
    :param pydantic_model: Pydantic model to populate with results returned from Nintex API.
    """

    sd = instance_start_data(instance_id=instance_id)
    return pydantic_model(**sd)


# TODO Delete instance
