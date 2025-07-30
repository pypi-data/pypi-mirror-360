from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.models_list_versions_body import ModelsListVersionsBody
from ...models.models_list_versions_response_200_item import (
    ModelsListVersionsResponse200Item,
)
from ...models.models_list_versions_response_400 import ModelsListVersionsResponse400
from ...models.models_list_versions_response_401 import ModelsListVersionsResponse401
from ...models.models_list_versions_response_500 import ModelsListVersionsResponse500
from ...types import Response


def _get_kwargs(
    *,
    body: ModelsListVersionsBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/v1/api/models/list_versions",
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        List["ModelsListVersionsResponse200Item"],
        ModelsListVersionsResponse400,
        ModelsListVersionsResponse401,
        ModelsListVersionsResponse500,
    ]
]:
    if response.status_code == HTTPStatus.OK:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ModelsListVersionsResponse200Item.from_dict(
                response_200_item_data
            )

            response_200.append(response_200_item)

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = ModelsListVersionsResponse400.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = ModelsListVersionsResponse401.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = ModelsListVersionsResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        List["ModelsListVersionsResponse200Item"],
        ModelsListVersionsResponse400,
        ModelsListVersionsResponse401,
        ModelsListVersionsResponse500,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelsListVersionsBody,
) -> Response[
    Union[
        List["ModelsListVersionsResponse200Item"],
        ModelsListVersionsResponse400,
        ModelsListVersionsResponse401,
        ModelsListVersionsResponse500,
    ]
]:
    """Retrieve versions of a model

     Returns all versions for a given model.

    Args:
        body (ModelsListVersionsBody):  Request for getting model versions

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[List['ModelsListVersionsResponse200Item'], ModelsListVersionsResponse400, ModelsListVersionsResponse401, ModelsListVersionsResponse500]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelsListVersionsBody,
) -> Optional[
    Union[
        List["ModelsListVersionsResponse200Item"],
        ModelsListVersionsResponse400,
        ModelsListVersionsResponse401,
        ModelsListVersionsResponse500,
    ]
]:
    """Retrieve versions of a model

     Returns all versions for a given model.

    Args:
        body (ModelsListVersionsBody):  Request for getting model versions

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[List['ModelsListVersionsResponse200Item'], ModelsListVersionsResponse400, ModelsListVersionsResponse401, ModelsListVersionsResponse500]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelsListVersionsBody,
) -> Response[
    Union[
        List["ModelsListVersionsResponse200Item"],
        ModelsListVersionsResponse400,
        ModelsListVersionsResponse401,
        ModelsListVersionsResponse500,
    ]
]:
    """Retrieve versions of a model

     Returns all versions for a given model.

    Args:
        body (ModelsListVersionsBody):  Request for getting model versions

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[List['ModelsListVersionsResponse200Item'], ModelsListVersionsResponse400, ModelsListVersionsResponse401, ModelsListVersionsResponse500]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ModelsListVersionsBody,
) -> Optional[
    Union[
        List["ModelsListVersionsResponse200Item"],
        ModelsListVersionsResponse400,
        ModelsListVersionsResponse401,
        ModelsListVersionsResponse500,
    ]
]:
    """Retrieve versions of a model

     Returns all versions for a given model.

    Args:
        body (ModelsListVersionsBody):  Request for getting model versions

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[List['ModelsListVersionsResponse200Item'], ModelsListVersionsResponse400, ModelsListVersionsResponse401, ModelsListVersionsResponse500]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
