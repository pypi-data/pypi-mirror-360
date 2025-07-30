import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status_initialized_status import StatusInitializedStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="StatusInitialized")


@_attrs_define
class StatusInitialized:
    """
    Attributes:
        initialized (datetime.datetime):
        status (Union[Unset, StatusInitializedStatus]):
    """

    initialized: datetime.datetime
    status: Union[Unset, StatusInitializedStatus] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        initialized = self.initialized.isoformat()

        status: Union[Unset, str] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "initialized": initialized,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        initialized = isoparse(d.pop("initialized"))

        _status = d.pop("status", UNSET)
        status: Union[Unset, StatusInitializedStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = StatusInitializedStatus(_status)

        status_initialized = cls(
            initialized=initialized,
            status=status,
        )

        status_initialized.additional_properties = d
        return status_initialized

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
