from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.export_collaborator_response_400 import ExportCollaboratorResponse400
from ...models.export_collaborator_response_404 import ExportCollaboratorResponse404
from ...types import UNSET, Response, Unset


def _get_kwargs(
    collaborator_id: str,
    *,
    sign: Union[Unset, bool] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["sign"] = sign

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/collaborators/{collaborator_id}/export",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = ExportCollaboratorResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = ExportCollaboratorResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    sign: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]]:
    """Export Data Consumer

    Args:
        collaborator_id (str):
        sign (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]]
    """

    kwargs = _get_kwargs(
        collaborator_id=collaborator_id,
        sign=sign,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    sign: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]]:
    """Export Data Consumer

    Args:
        collaborator_id (str):
        sign (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]
    """

    return sync_detailed(
        collaborator_id=collaborator_id,
        client=client,
        sign=sign,
    ).parsed


async def asyncio_detailed(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    sign: Union[Unset, bool] = UNSET,
) -> Response[Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]]:
    """Export Data Consumer

    Args:
        collaborator_id (str):
        sign (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]]
    """

    kwargs = _get_kwargs(
        collaborator_id=collaborator_id,
        sign=sign,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    sign: Union[Unset, bool] = UNSET,
) -> Optional[Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]]:
    """Export Data Consumer

    Args:
        collaborator_id (str):
        sign (Union[Unset, bool]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, ExportCollaboratorResponse400, ExportCollaboratorResponse404]
    """

    return (
        await asyncio_detailed(
            collaborator_id=collaborator_id,
            client=client,
            sign=sign,
        )
    ).parsed
