import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.pending_report_status import PendingReportStatus

T = TypeVar("T", bound="PendingReport")


@_attrs_define
class PendingReport:
    """
    Attributes:
        id (str):
        status (PendingReportStatus):
        collaborator_id (str):
        mount (datetime.datetime):
        start (datetime.datetime):
    """

    id: str
    status: PendingReportStatus
    collaborator_id: str
    mount: datetime.datetime
    start: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        status = self.status.value

        collaborator_id = self.collaborator_id

        mount = self.mount.isoformat()

        start = self.start.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "collaboratorId": collaborator_id,
                "mount": mount,
                "start": start,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        status = PendingReportStatus(d.pop("status"))

        collaborator_id = d.pop("collaboratorId")

        mount = isoparse(d.pop("mount"))

        start = isoparse(d.pop("start"))

        pending_report = cls(
            id=id,
            status=status,
            collaborator_id=collaborator_id,
            mount=mount,
            start=start,
        )

        pending_report.additional_properties = d
        return pending_report

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
