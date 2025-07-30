from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.equal import Equal
    from ..models.expression_type_2 import ExpressionType2
    from ..models.expression_type_3 import ExpressionType3
    from ..models.greater_than import GreaterThan
    from ..models.property_ import Property
    from ..models.query_collaborator_body_join_item import QueryCollaboratorBodyJoinItem
    from ..models.query_collaborator_body_select_item import QueryCollaboratorBodySelectItem


T = TypeVar("T", bound="QueryCollaboratorBody")


@_attrs_define
class QueryCollaboratorBody:
    """
    Attributes:
        select (Union[Unset, list['QueryCollaboratorBodySelectItem']]): If no select clause is passed it will be
            interpreted as "SELECT *"
        where (Union['Equal', 'ExpressionType2', 'ExpressionType3', 'GreaterThan', 'Property', Unset]):
        limit (Union[Unset, float]):
        join (Union[Unset, list['QueryCollaboratorBodyJoinItem']]):
    """

    select: Union[Unset, list["QueryCollaboratorBodySelectItem"]] = UNSET
    where: Union["Equal", "ExpressionType2", "ExpressionType3", "GreaterThan", "Property", Unset] = UNSET
    limit: Union[Unset, float] = UNSET
    join: Union[Unset, list["QueryCollaboratorBodyJoinItem"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.equal import Equal
        from ..models.expression_type_2 import ExpressionType2
        from ..models.expression_type_3 import ExpressionType3
        from ..models.property_ import Property

        select: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.select, Unset):
            select = []
            for select_item_data in self.select:
                select_item = select_item_data.to_dict()
                select.append(select_item)

        where: Union[Unset, dict[str, Any]]
        if isinstance(self.where, Unset):
            where = UNSET
        elif isinstance(self.where, Equal):
            where = self.where.to_dict()
        elif isinstance(self.where, Property):
            where = self.where.to_dict()
        elif isinstance(self.where, ExpressionType2):
            where = self.where.to_dict()
        elif isinstance(self.where, ExpressionType3):
            where = self.where.to_dict()
        else:
            where = self.where.to_dict()

        limit = self.limit

        join: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.join, Unset):
            join = []
            for join_item_data in self.join:
                join_item = join_item_data.to_dict()
                join.append(join_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if select is not UNSET:
            field_dict["select"] = select
        if where is not UNSET:
            field_dict["where"] = where
        if limit is not UNSET:
            field_dict["limit"] = limit
        if join is not UNSET:
            field_dict["join"] = join

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.equal import Equal
        from ..models.expression_type_2 import ExpressionType2
        from ..models.expression_type_3 import ExpressionType3
        from ..models.greater_than import GreaterThan
        from ..models.property_ import Property
        from ..models.query_collaborator_body_join_item import QueryCollaboratorBodyJoinItem
        from ..models.query_collaborator_body_select_item import QueryCollaboratorBodySelectItem

        d = dict(src_dict)
        select = []
        _select = d.pop("select", UNSET)
        for select_item_data in _select or []:
            select_item = QueryCollaboratorBodySelectItem.from_dict(select_item_data)

            select.append(select_item)

        def _parse_where(
            data: object,
        ) -> Union["Equal", "ExpressionType2", "ExpressionType3", "GreaterThan", "Property", Unset]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_expression_type_0 = Equal.from_dict(data)

                return componentsschemas_expression_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_expression_type_1 = Property.from_dict(data)

                return componentsschemas_expression_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_expression_type_2 = ExpressionType2.from_dict(data)

                return componentsschemas_expression_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_expression_type_3 = ExpressionType3.from_dict(data)

                return componentsschemas_expression_type_3
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_expression_type_4 = GreaterThan.from_dict(data)

            return componentsschemas_expression_type_4

        where = _parse_where(d.pop("where", UNSET))

        limit = d.pop("limit", UNSET)

        join = []
        _join = d.pop("join", UNSET)
        for join_item_data in _join or []:
            join_item = QueryCollaboratorBodyJoinItem.from_dict(join_item_data)

            join.append(join_item)

        query_collaborator_body = cls(
            select=select,
            where=where,
            limit=limit,
            join=join,
        )

        query_collaborator_body.additional_properties = d
        return query_collaborator_body

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
