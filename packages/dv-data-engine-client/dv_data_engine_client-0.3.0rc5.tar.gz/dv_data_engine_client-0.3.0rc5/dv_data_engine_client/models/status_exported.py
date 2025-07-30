import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status_exported_status import StatusExportedStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="StatusExported")


@_attrs_define
class StatusExported:
    """
    Attributes:
        initialized (datetime.datetime):
        write_start (datetime.datetime):
        mounted (datetime.datetime):
        export_start (datetime.datetime):
        exported (datetime.datetime):
        status (Union[Unset, StatusExportedStatus]):
    """

    initialized: datetime.datetime
    write_start: datetime.datetime
    mounted: datetime.datetime
    export_start: datetime.datetime
    exported: datetime.datetime
    status: Union[Unset, StatusExportedStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        initialized = self.initialized.isoformat()

        write_start = self.write_start.isoformat()

        mounted = self.mounted.isoformat()

        export_start = self.export_start.isoformat()

        exported = self.exported.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "initialized": initialized,
                "writeStart": write_start,
                "mounted": mounted,
                "exportStart": export_start,
                "exported": exported,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        initialized = isoparse(d.pop("initialized"))

        write_start = isoparse(d.pop("writeStart"))

        mounted = isoparse(d.pop("mounted"))

        export_start = isoparse(d.pop("exportStart"))

        exported = isoparse(d.pop("exported"))

        _status = d.pop("status", UNSET)
        status: Union[Unset, StatusExportedStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = StatusExportedStatus(_status)

        status_exported = cls(
            initialized=initialized,
            write_start=write_start,
            mounted=mounted,
            export_start=export_start,
            exported=exported,
            status=status,
        )

        status_exported.additional_properties = d
        return status_exported

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
