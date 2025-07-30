from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.mount_collaborator_response_400 import MountCollaboratorResponse400
from ...models.mount_collaborator_response_404 import MountCollaboratorResponse404
from ...types import Response


def _get_kwargs(
    collaborator_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/collaborators/{collaborator_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = MountCollaboratorResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = MountCollaboratorResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]]:
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
) -> Response[Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]]:
    """Mount a new collaborator

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]]
    """

    kwargs = _get_kwargs(
        collaborator_id=collaborator_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]]:
    """Mount a new collaborator

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]
    """

    return sync_detailed(
        collaborator_id=collaborator_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]]:
    """Mount a new collaborator

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]]
    """

    kwargs = _get_kwargs(
        collaborator_id=collaborator_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]]:
    """Mount a new collaborator

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, MountCollaboratorResponse400, MountCollaboratorResponse404]
    """

    return (
        await asyncio_detailed(
            collaborator_id=collaborator_id,
            client=client,
        )
    ).parsed
