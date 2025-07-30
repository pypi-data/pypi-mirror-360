from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.query_collaborator_body import QueryCollaboratorBody
from ...models.query_collaborator_response_400 import QueryCollaboratorResponse400
from ...models.query_collaborator_response_404 import QueryCollaboratorResponse404
from ...types import Response


def _get_kwargs(
    collaborator_id: str,
    *,
    body: QueryCollaboratorBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/collaborators/{collaborator_id}/query",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]]:
    if response.status_code == 200:
        response_200 = response.text
        return response_200
    if response.status_code == 400:
        response_400 = QueryCollaboratorResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = QueryCollaboratorResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]]:
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
    body: QueryCollaboratorBody,
) -> Response[Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]]:
    """Query on a collaborator

    Args:
        collaborator_id (str):
        body (QueryCollaboratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]]
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
    body: QueryCollaboratorBody,
) -> Optional[Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]]:
    """Query on a collaborator

    Args:
        collaborator_id (str):
        body (QueryCollaboratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]
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
    body: QueryCollaboratorBody,
) -> Response[Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]]:
    """Query on a collaborator

    Args:
        collaborator_id (str):
        body (QueryCollaboratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]]
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
    body: QueryCollaboratorBody,
) -> Optional[Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]]:
    """Query on a collaborator

    Args:
        collaborator_id (str):
        body (QueryCollaboratorBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[QueryCollaboratorResponse400, QueryCollaboratorResponse404, str]
    """

    return (
        await asyncio_detailed(
            collaborator_id=collaborator_id,
            client=client,
            body=body,
        )
    ).parsed
