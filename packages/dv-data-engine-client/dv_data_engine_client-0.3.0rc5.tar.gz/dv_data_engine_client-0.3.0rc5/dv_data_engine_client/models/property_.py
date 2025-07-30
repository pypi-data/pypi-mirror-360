from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Property")


@_attrs_define
class Property:
    """
    Attributes:
        property_ (str):
        collaborator_id (Union[Unset, str]):
    """

    property_: str
    collaborator_id: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_ = self.property_

        collaborator_id = self.collaborator_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "property": property_,
            }
        )
        if collaborator_id is not UNSET:
            field_dict["collaboratorId"] = collaborator_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        property_ = d.pop("property")

        collaborator_id = d.pop("collaboratorId", UNSET)

        property_ = cls(
            property_=property_,
            collaborator_id=collaborator_id,
        )

        property_.additional_properties = d
        return property_

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
