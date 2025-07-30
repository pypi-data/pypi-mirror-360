from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.equal import Equal
    from ..models.expression_type_2 import ExpressionType2
    from ..models.expression_type_3 import ExpressionType3
    from ..models.property_ import Property


T = TypeVar("T", bound="GreaterThan")


@_attrs_define
class GreaterThan:
    """
    Attributes:
        gt_a (Union['Equal', 'ExpressionType2', 'ExpressionType3', 'GreaterThan', 'Property', Unset]):
        gt_b (Union['Equal', 'ExpressionType2', 'ExpressionType3', 'GreaterThan', 'Property', Unset]):
    """

    gt_a: Union["Equal", "ExpressionType2", "ExpressionType3", "GreaterThan", "Property", Unset] = UNSET
    gt_b: Union["Equal", "ExpressionType2", "ExpressionType3", "GreaterThan", "Property", Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.equal import Equal
        from ..models.expression_type_2 import ExpressionType2
        from ..models.expression_type_3 import ExpressionType3
        from ..models.property_ import Property

        gt_a: Union[Unset, dict[str, Any]]
        if isinstance(self.gt_a, Unset):
            gt_a = UNSET
        elif isinstance(self.gt_a, Equal):
            gt_a = self.gt_a.to_dict()
        elif isinstance(self.gt_a, Property):
            gt_a = self.gt_a.to_dict()
        elif isinstance(self.gt_a, ExpressionType2):
            gt_a = self.gt_a.to_dict()
        elif isinstance(self.gt_a, ExpressionType3):
            gt_a = self.gt_a.to_dict()
        else:
            gt_a = self.gt_a.to_dict()

        gt_b: Union[Unset, dict[str, Any]]
        if isinstance(self.gt_b, Unset):
            gt_b = UNSET
        elif isinstance(self.gt_b, Equal):
            gt_b = self.gt_b.to_dict()
        elif isinstance(self.gt_b, Property):
            gt_b = self.gt_b.to_dict()
        elif isinstance(self.gt_b, ExpressionType2):
            gt_b = self.gt_b.to_dict()
        elif isinstance(self.gt_b, ExpressionType3):
            gt_b = self.gt_b.to_dict()
        else:
            gt_b = self.gt_b.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if gt_a is not UNSET:
            field_dict["gtA"] = gt_a
        if gt_b is not UNSET:
            field_dict["gtB"] = gt_b

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.equal import Equal
        from ..models.expression_type_2 import ExpressionType2
        from ..models.expression_type_3 import ExpressionType3
        from ..models.property_ import Property

        d = dict(src_dict)

        def _parse_gt_a(
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

        gt_a = _parse_gt_a(d.pop("gtA", UNSET))

        def _parse_gt_b(
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

        gt_b = _parse_gt_b(d.pop("gtB", UNSET))

        greater_than = cls(
            gt_a=gt_a,
            gt_b=gt_b,
        )

        greater_than.additional_properties = d
        return greater_than

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
