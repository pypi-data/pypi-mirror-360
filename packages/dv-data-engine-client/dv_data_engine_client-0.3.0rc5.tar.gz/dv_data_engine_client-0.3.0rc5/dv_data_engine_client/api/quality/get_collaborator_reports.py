from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.finished_summary import FinishedSummary
from ...models.get_collaborator_reports_response_400 import GetCollaboratorReportsResponse400
from ...models.get_collaborator_reports_response_404 import GetCollaboratorReportsResponse404
from ...models.pending_report import PendingReport
from ...types import Response


def _get_kwargs(
    collaborator_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/collaborators/{collaborator_id}/quality",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetCollaboratorReportsResponse400,
        GetCollaboratorReportsResponse404,
        list[Union["FinishedSummary", "PendingReport"]],
    ]
]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:

            def _parse_response_200_item(data: object) -> Union["FinishedSummary", "PendingReport"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_quality_report_summary_type_0 = PendingReport.from_dict(data)

                    return componentsschemas_quality_report_summary_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_quality_report_summary_type_1 = FinishedSummary.from_dict(data)

                return componentsschemas_quality_report_summary_type_1

            response_200_item = _parse_response_200_item(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 400:
        response_400 = GetCollaboratorReportsResponse400.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = GetCollaboratorReportsResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[
    Union[
        GetCollaboratorReportsResponse400,
        GetCollaboratorReportsResponse404,
        list[Union["FinishedSummary", "PendingReport"]],
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
        GetCollaboratorReportsResponse400,
        GetCollaboratorReportsResponse404,
        list[Union["FinishedSummary", "PendingReport"]],
    ]
]:
    """Get Collaborator Reports

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetCollaboratorReportsResponse400, GetCollaboratorReportsResponse404, list[Union['FinishedSummary', 'PendingReport']]]]
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
        GetCollaboratorReportsResponse400,
        GetCollaboratorReportsResponse404,
        list[Union["FinishedSummary", "PendingReport"]],
    ]
]:
    """Get Collaborator Reports

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetCollaboratorReportsResponse400, GetCollaboratorReportsResponse404, list[Union['FinishedSummary', 'PendingReport']]]
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
        GetCollaboratorReportsResponse400,
        GetCollaboratorReportsResponse404,
        list[Union["FinishedSummary", "PendingReport"]],
    ]
]:
    """Get Collaborator Reports

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetCollaboratorReportsResponse400, GetCollaboratorReportsResponse404, list[Union['FinishedSummary', 'PendingReport']]]]
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
        GetCollaboratorReportsResponse400,
        GetCollaboratorReportsResponse404,
        list[Union["FinishedSummary", "PendingReport"]],
    ]
]:
    """Get Collaborator Reports

    Args:
        collaborator_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetCollaboratorReportsResponse400, GetCollaboratorReportsResponse404, list[Union['FinishedSummary', 'PendingReport']]]
    """

    return (
        await asyncio_detailed(
            collaborator_id=collaborator_id,
            client=client,
        )
    ).parsed
