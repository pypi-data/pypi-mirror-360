from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.pipelines_get_logs_body import PipelinesGetLogsBody
from ...models.pipelines_get_logs_response_400 import PipelinesGetLogsResponse400
from ...models.pipelines_get_logs_response_401 import PipelinesGetLogsResponse401
from ...models.pipelines_get_logs_response_500 import PipelinesGetLogsResponse500
from ...models.pipelines_get_logs_response_502 import PipelinesGetLogsResponse502
from ...types import Response


def _get_kwargs(
    *,
    body: PipelinesGetLogsBody,
) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    _kwargs: Dict[str, Any] = {
        "method": "post",
        "url": "/v1/api/pipelines/get_logs",
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
        Any,
        PipelinesGetLogsResponse400,
        PipelinesGetLogsResponse401,
        PipelinesGetLogsResponse500,
        PipelinesGetLogsResponse502,
    ]
]:
    if response.status_code == HTTPStatus.OK:
        response_200 = cast(Any, None)
        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = PipelinesGetLogsResponse400.from_dict(response.json())

        return response_400
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = PipelinesGetLogsResponse401.from_dict(response.json())

        return response_401
    if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
        response_500 = PipelinesGetLogsResponse500.from_dict(response.json())

        return response_500
    if response.status_code == HTTPStatus.BAD_GATEWAY:
        response_502 = PipelinesGetLogsResponse502.from_dict(response.json())

        return response_502
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        Any,
        PipelinesGetLogsResponse400,
        PipelinesGetLogsResponse401,
        PipelinesGetLogsResponse500,
        PipelinesGetLogsResponse502,
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
    body: PipelinesGetLogsBody,
) -> Response[
    Union[
        Any,
        PipelinesGetLogsResponse400,
        PipelinesGetLogsResponse401,
        PipelinesGetLogsResponse500,
        PipelinesGetLogsResponse502,
    ]
]:
    """Fetch pipeline logs

     Fetch pipeline logs.

    Args:
        body (PipelinesGetLogsBody):  Request to retrieve inference logs for a pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]
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
    body: PipelinesGetLogsBody,
) -> Optional[
    Union[
        Any,
        PipelinesGetLogsResponse400,
        PipelinesGetLogsResponse401,
        PipelinesGetLogsResponse500,
        PipelinesGetLogsResponse502,
    ]
]:
    """Fetch pipeline logs

     Fetch pipeline logs.

    Args:
        body (PipelinesGetLogsBody):  Request to retrieve inference logs for a pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PipelinesGetLogsBody,
) -> Response[
    Union[
        Any,
        PipelinesGetLogsResponse400,
        PipelinesGetLogsResponse401,
        PipelinesGetLogsResponse500,
        PipelinesGetLogsResponse502,
    ]
]:
    """Fetch pipeline logs

     Fetch pipeline logs.

    Args:
        body (PipelinesGetLogsBody):  Request to retrieve inference logs for a pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: PipelinesGetLogsBody,
) -> Optional[
    Union[
        Any,
        PipelinesGetLogsResponse400,
        PipelinesGetLogsResponse401,
        PipelinesGetLogsResponse500,
        PipelinesGetLogsResponse502,
    ]
]:
    """Fetch pipeline logs

     Fetch pipeline logs.

    Args:
        body (PipelinesGetLogsBody):  Request to retrieve inference logs for a pipeline.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PipelinesGetLogsResponse400, PipelinesGetLogsResponse401, PipelinesGetLogsResponse500, PipelinesGetLogsResponse502]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
