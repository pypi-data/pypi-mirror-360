from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.equal import Equal


T = TypeVar("T", bound="QueryCollaboratorBodyJoinItem")


@_attrs_define
class QueryCollaboratorBodyJoinItem:
    """
    Attributes:
        join_collaborator_id (str):
        join_on (Equal):
    """

    join_collaborator_id: str
    join_on: "Equal"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        join_collaborator_id = self.join_collaborator_id

        join_on = self.join_on.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "joinCollaboratorId": join_collaborator_id,
                "joinOn": join_on,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.equal import Equal

        d = dict(src_dict)
        join_collaborator_id = d.pop("joinCollaboratorId")

        join_on = Equal.from_dict(d.pop("joinOn"))

        query_collaborator_body_join_item = cls(
            join_collaborator_id=join_collaborator_id,
            join_on=join_on,
        )

        query_collaborator_body_join_item.additional_properties = d
        return query_collaborator_body_join_item

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
