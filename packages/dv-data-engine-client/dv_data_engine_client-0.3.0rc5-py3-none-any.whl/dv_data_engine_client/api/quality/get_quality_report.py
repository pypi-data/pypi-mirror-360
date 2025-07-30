from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.finished_report import FinishedReport
from ...models.get_quality_report_response_404 import GetQualityReportResponse404
from ...models.pending_report import PendingReport
from ...types import Response


def _get_kwargs(
    report_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/quality-report/{report_id}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[GetQualityReportResponse404, Union["FinishedReport", "PendingReport"]]]:
    if response.status_code == 200:

        def _parse_response_200(data: object) -> Union["FinishedReport", "PendingReport"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_quality_report_type_0 = PendingReport.from_dict(data)

                return componentsschemas_quality_report_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_quality_report_type_1 = FinishedReport.from_dict(data)

            return componentsschemas_quality_report_type_1

        response_200 = _parse_response_200(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = GetQualityReportResponse404.from_dict(response.json())

        return response_404
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[GetQualityReportResponse404, Union["FinishedReport", "PendingReport"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    report_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[GetQualityReportResponse404, Union["FinishedReport", "PendingReport"]]]:
    """Get Quality Report

    Args:
        report_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetQualityReportResponse404, Union['FinishedReport', 'PendingReport']]]
    """

    kwargs = _get_kwargs(
        report_id=report_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    report_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[GetQualityReportResponse404, Union["FinishedReport", "PendingReport"]]]:
    """Get Quality Report

    Args:
        report_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetQualityReportResponse404, Union['FinishedReport', 'PendingReport']]
    """

    return sync_detailed(
        report_id=report_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    report_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[GetQualityReportResponse404, Union["FinishedReport", "PendingReport"]]]:
    """Get Quality Report

    Args:
        report_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetQualityReportResponse404, Union['FinishedReport', 'PendingReport']]]
    """

    kwargs = _get_kwargs(
        report_id=report_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    report_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[GetQualityReportResponse404, Union["FinishedReport", "PendingReport"]]]:
    """Get Quality Report

    Args:
        report_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetQualityReportResponse404, Union['FinishedReport', 'PendingReport']]
    """

    return (
        await asyncio_detailed(
            report_id=report_id,
            client=client,
        )
    ).parsed
