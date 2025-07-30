from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_orchestration_by_id_response import GetOrchestrationByIdResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    id: str,
    token: str,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {}

    params["id"] = id

    params["token"] = token

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: Dict[str, Any] = {
        "method": "get",
        "url": "/v1/api/orchestration/download",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[GetOrchestrationByIdResponse]:
    if response.status_code == HTTPStatus.OK:
        response_200 = GetOrchestrationByIdResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[GetOrchestrationByIdResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    id: str,
    token: str,
) -> Response[GetOrchestrationByIdResponse]:
    """
    Args:
        id (str):
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetOrchestrationByIdResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        token=token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    id: str,
    token: str,
) -> Optional[GetOrchestrationByIdResponse]:
    """
    Args:
        id (str):
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetOrchestrationByIdResponse
    """

    return sync_detailed(
        client=client,
        id=id,
        token=token,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    id: str,
    token: str,
) -> Response[GetOrchestrationByIdResponse]:
    """
    Args:
        id (str):
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetOrchestrationByIdResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        token=token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    id: str,
    token: str,
) -> Optional[GetOrchestrationByIdResponse]:
    """
    Args:
        id (str):
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetOrchestrationByIdResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            id=id,
            token=token,
        )
    ).parsed
