from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.collaborator_status_response_404 import CollaboratorStatusResponse404
from ...models.status_error import StatusError
from ...models.status_exported import StatusExported
from ...models.status_exporting import StatusExporting
from ...models.status_initialized import StatusInitialized
from ...models.status_mounted import StatusMounted
from ...models.status_unmounted import StatusUnmounted
from ...models.status_writing import StatusWriting
from ...types import Response


def _get_kwargs(
    collaborator_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/collaborators/{collaborator_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        CollaboratorStatusResponse404,
        Union[
            "StatusError",
            "StatusExported",
            "StatusExporting",
            "StatusInitialized",
            "StatusMounted",
            "StatusUnmounted",
            "StatusWriting",
        ],
    ]
]:
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> Union[
            "StatusError",
            "StatusExported",
            "StatusExporting",
            "StatusInitialized",
            "StatusMounted",
            "StatusUnmounted",
            "StatusWriting",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_0 = StatusUnmounted.from_dict(data)

                return componentsschemas_status_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_1 = StatusInitialized.from_dict(data)

                return componentsschemas_status_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_2 = StatusWriting.from_dict(data)

                return componentsschemas_status_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_3 = StatusMounted.from_dict(data)

                return componentsschemas_status_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_4 = StatusExporting.from_dict(data)

                return componentsschemas_status_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_status_type_5 = StatusExported.from_dict(data)

                return componentsschemas_status_type_5
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_status_type_6 = StatusError.from_dict(data)

            return componentsschemas_status_type_6

        response_200 = _parse_response_200(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = CollaboratorStatusResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        CollaboratorStatusResponse404,
        Union[
            "StatusError",
            "StatusExported",
            "StatusExporting",
            "StatusInitialized",
            "StatusMounted",
            "StatusUnmounted",
            "StatusWriting",
        ],
    ]
]:
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
) -> Response[
    Union[
        CollaboratorStatusResponse404,
        Union[
            "StatusError",
            "StatusExported",
            "StatusExporting",
            "StatusInitialized",
            "StatusMounted",
            "StatusUnmounted",
            "StatusWriting",
        ],
    ]
]:
    """Status of a collaborator in the data engine

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollaboratorStatusResponse404, Union['StatusError', 'StatusExported', 'StatusExporting', 'StatusInitialized', 'StatusMounted', 'StatusUnmounted', 'StatusWriting']]]
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
) -> Optional[
    Union[
        CollaboratorStatusResponse404,
        Union[
            "StatusError",
            "StatusExported",
            "StatusExporting",
            "StatusInitialized",
            "StatusMounted",
            "StatusUnmounted",
            "StatusWriting",
        ],
    ]
]:
    """Status of a collaborator in the data engine

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollaboratorStatusResponse404, Union['StatusError', 'StatusExported', 'StatusExporting', 'StatusInitialized', 'StatusMounted', 'StatusUnmounted', 'StatusWriting']]
    """

    return sync_detailed(
        collaborator_id=collaborator_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    collaborator_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[
    Union[
        CollaboratorStatusResponse404,
        Union[
            "StatusError",
            "StatusExported",
            "StatusExporting",
            "StatusInitialized",
            "StatusMounted",
            "StatusUnmounted",
            "StatusWriting",
        ],
    ]
]:
    """Status of a collaborator in the data engine

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CollaboratorStatusResponse404, Union['StatusError', 'StatusExported', 'StatusExporting', 'StatusInitialized', 'StatusMounted', 'StatusUnmounted', 'StatusWriting']]]
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
) -> Optional[
    Union[
        CollaboratorStatusResponse404,
        Union[
            "StatusError",
            "StatusExported",
            "StatusExporting",
            "StatusInitialized",
            "StatusMounted",
            "StatusUnmounted",
            "StatusWriting",
        ],
    ]
]:
    """Status of a collaborator in the data engine

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CollaboratorStatusResponse404, Union['StatusError', 'StatusExported', 'StatusExporting', 'StatusInitialized', 'StatusMounted', 'StatusUnmounted', 'StatusWriting']]
    """

    return (
        await asyncio_detailed(
            collaborator_id=collaborator_id,
            client=client,
        )
    ).parsed
