from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.expression_type_2 import ExpressionType2
    from ..models.expression_type_3 import ExpressionType3
    from ..models.greater_than import GreaterThan
    from ..models.property_ import Property


T = TypeVar("T", bound="Equal")


@_attrs_define
class Equal:
    """
    Attributes:
        equal_a (Union['Equal', 'ExpressionType2', 'ExpressionType3', 'GreaterThan', 'Property', Unset]):
        equal_b (Union['Equal', 'ExpressionType2', 'ExpressionType3', 'GreaterThan', 'Property', Unset]):
    """

    equal_a: Union["Equal", "ExpressionType2", "ExpressionType3", "GreaterThan", "Property", Unset] = UNSET
    equal_b: Union["Equal", "ExpressionType2", "ExpressionType3", "GreaterThan", "Property", Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.expression_type_2 import ExpressionType2
        from ..models.expression_type_3 import ExpressionType3
        from ..models.property_ import Property

        equal_a: Union[Unset, dict[str, Any]]
        if isinstance(self.equal_a, Unset):
            equal_a = UNSET
        elif isinstance(self.equal_a, Equal):
            equal_a = self.equal_a.to_dict()
        elif isinstance(self.equal_a, Property):
            equal_a = self.equal_a.to_dict()
        elif isinstance(self.equal_a, ExpressionType2):
            equal_a = self.equal_a.to_dict()
        elif isinstance(self.equal_a, ExpressionType3):
            equal_a = self.equal_a.to_dict()
        else:
            equal_a = self.equal_a.to_dict()

        equal_b: Union[Unset, dict[str, Any]]
        if isinstance(self.equal_b, Unset):
            equal_b = UNSET
        elif isinstance(self.equal_b, Equal):
            equal_b = self.equal_b.to_dict()
        elif isinstance(self.equal_b, Property):
            equal_b = self.equal_b.to_dict()
        elif isinstance(self.equal_b, ExpressionType2):
            equal_b = self.equal_b.to_dict()
        elif isinstance(self.equal_b, ExpressionType3):
            equal_b = self.equal_b.to_dict()
        else:
            equal_b = self.equal_b.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if equal_a is not UNSET:
            field_dict["equalA"] = equal_a
        if equal_b is not UNSET:
            field_dict["equalB"] = equal_b

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.expression_type_2 import ExpressionType2
        from ..models.expression_type_3 import ExpressionType3
        from ..models.greater_than import GreaterThan
        from ..models.property_ import Property

        d = dict(src_dict)

        def _parse_equal_a(
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

        equal_a = _parse_equal_a(d.pop("equalA", UNSET))

        def _parse_equal_b(
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

        equal_b = _parse_equal_b(d.pop("equalB", UNSET))

        equal = cls(
            equal_a=equal_a,
            equal_b=equal_b,
        )

        equal.additional_properties = d
        return equal

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
