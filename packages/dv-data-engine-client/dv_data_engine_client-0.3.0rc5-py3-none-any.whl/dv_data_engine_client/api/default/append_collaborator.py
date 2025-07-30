from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.append_collaborator_body import AppendCollaboratorBody
from ...models.append_collaborator_response_400 import AppendCollaboratorResponse400
from ...models.append_collaborator_response_404 import AppendCollaboratorResponse404
from ...types import Response


def _get_kwargs(
    collaborator_id: str,
    *,
    body: AppendCollaboratorBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": f"/collaborators/{collaborator_id}/append",
    }

    _kwargs["files"] = body.to_multipart()

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 400:
        response_400 = AppendCollaboratorResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = AppendCollaboratorResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]]:
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
    body: AppendCollaboratorBody,
) -> Response[Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]]:
    """Append data on a Data Consumer

    Args:
        collaborator_id (str):
        body (AppendCollaboratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]]
    """

    kwargs = _get_kwargs(
        collaborator_id=collaborator_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AppendCollaboratorBody,
) -> Optional[Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]]:
    """Append data on a Data Consumer

    Args:
        collaborator_id (str):
        body (AppendCollaboratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]
    """

    return sync_detailed(
        collaborator_id=collaborator_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AppendCollaboratorBody,
) -> Response[Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]]:
    """Append data on a Data Consumer

    Args:
        collaborator_id (str):
        body (AppendCollaboratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]]
    """

    kwargs = _get_kwargs(
        collaborator_id=collaborator_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: AppendCollaboratorBody,
) -> Optional[Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]]:
    """Append data on a Data Consumer

    Args:
        collaborator_id (str):
        body (AppendCollaboratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, AppendCollaboratorResponse400, AppendCollaboratorResponse404]
    """

    return (
        await asyncio_detailed(
            collaborator_id=collaborator_id,
            client=client,
            body=body,
        )
    ).parsed
