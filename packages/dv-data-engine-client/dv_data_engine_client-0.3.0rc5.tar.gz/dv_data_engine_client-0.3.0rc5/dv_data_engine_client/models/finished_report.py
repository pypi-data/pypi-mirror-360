import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.finished_report_status import FinishedReportStatus

if TYPE_CHECKING:
    from ..models.finished_report_error_item import FinishedReportErrorItem
    from ..models.finished_report_fail_item import FinishedReportFailItem
    from ..models.finished_report_success_item import FinishedReportSuccessItem


T = TypeVar("T", bound="FinishedReport")


@_attrs_define
class FinishedReport:
    """
    Attributes:
        id (str):
        status (FinishedReportStatus):
        collaborator_id (str):
        mount (datetime.datetime):
        start (datetime.datetime):
        finish (datetime.datetime):
        success (list['FinishedReportSuccessItem']):
        fail (list['FinishedReportFailItem']):
        error (list['FinishedReportErrorItem']):
    """

    id: str
    status: FinishedReportStatus
    collaborator_id: str
    mount: datetime.datetime
    start: datetime.datetime
    finish: datetime.datetime
    success: list["FinishedReportSuccessItem"]
    fail: list["FinishedReportFailItem"]
    error: list["FinishedReportErrorItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status.value

        collaborator_id = self.collaborator_id

        mount = self.mount.isoformat()

        start = self.start.isoformat()

        finish = self.finish.isoformat()

        success = []
        for success_item_data in self.success:
            success_item = success_item_data.to_dict()
            success.append(success_item)

        fail = []
        for fail_item_data in self.fail:
            fail_item = fail_item_data.to_dict()
            fail.append(fail_item)

        error = []
        for error_item_data in self.error:
            error_item = error_item_data.to_dict()
            error.append(error_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "collaboratorId": collaborator_id,
                "mount": mount,
                "start": start,
                "finish": finish,
                "success": success,
                "fail": fail,
                "error": error,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.finished_report_error_item import FinishedReportErrorItem
        from ..models.finished_report_fail_item import FinishedReportFailItem
        from ..models.finished_report_success_item import FinishedReportSuccessItem

        d = dict(src_dict)
        id = d.pop("id")

        status = FinishedReportStatus(d.pop("status"))

        collaborator_id = d.pop("collaboratorId")

        mount = isoparse(d.pop("mount"))

        start = isoparse(d.pop("start"))

        finish = isoparse(d.pop("finish"))

        success = []
        _success = d.pop("success")
        for success_item_data in _success:
            success_item = FinishedReportSuccessItem.from_dict(success_item_data)

            success.append(success_item)

        fail = []
        _fail = d.pop("fail")
        for fail_item_data in _fail:
            fail_item = FinishedReportFailItem.from_dict(fail_item_data)

            fail.append(fail_item)

        error = []
        _error = d.pop("error")
        for error_item_data in _error:
            error_item = FinishedReportErrorItem.from_dict(error_item_data)

            error.append(error_item)

        finished_report = cls(
            id=id,
            status=status,
            collaborator_id=collaborator_id,
            mount=mount,
            start=start,
            finish=finish,
            success=success,
            fail=fail,
            error=error,
        )

        finished_report.additional_properties = d
        return finished_report

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
