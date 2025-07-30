from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.broadcaster_verify_token_response import BroadcasterVerifyTokenResponse
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    token: str,
) -> Dict[str, Any]:
    return {
        "method": "get",
        "url": "/broadcaster/verify/{token}".format(
            token=token,
        ),
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[BroadcasterVerifyTokenResponse, Error]]:
    if response.status_code == HTTPStatus.CREATED:
        response_201 = BroadcasterVerifyTokenResponse.from_dict(response.json())

        return response_201
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        response_401 = Error.from_dict(response.json())

        return response_401
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[BroadcasterVerifyTokenResponse, Error]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    token: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[BroadcasterVerifyTokenResponse, Error]]:
    """Verify token provided by broadcaster

    Args:
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BroadcasterVerifyTokenResponse, Error]]
    """

    kwargs = _get_kwargs(
        token=token,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    token: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[BroadcasterVerifyTokenResponse, Error]]:
    """Verify token provided by broadcaster

    Args:
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BroadcasterVerifyTokenResponse, Error]
    """

    return sync_detailed(
        token=token,
        client=client,
    ).parsed


async def asyncio_detailed(
    token: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[BroadcasterVerifyTokenResponse, Error]]:
    """Verify token provided by broadcaster

    Args:
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[BroadcasterVerifyTokenResponse, Error]]
    """

    kwargs = _get_kwargs(
        token=token,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    token: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[BroadcasterVerifyTokenResponse, Error]]:
    """Verify token provided by broadcaster

    Args:
        token (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[BroadcasterVerifyTokenResponse, Error]
    """

    return (
        await asyncio_detailed(
            token=token,
            client=client,
        )
    ).parsed
