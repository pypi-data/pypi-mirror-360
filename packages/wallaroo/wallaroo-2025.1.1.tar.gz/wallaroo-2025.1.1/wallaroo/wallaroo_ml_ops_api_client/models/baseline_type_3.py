from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="BaselineType3")


@_attrs_define
class BaselineType3:
    """
    Example:
        [1.0, 2.0, 3.0, 4.0, null]

    Attributes:
        vector (List[float]): Use a vector of values as a Baseline. This also supports null values that are converted to
            `f64::NAN`.
    """

    vector: List[float]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        vector = self.vector

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Vector": vector,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        vector = cast(List[float], d.pop("Vector"))

        baseline_type_3 = cls(
            vector=vector,
        )

        baseline_type_3.additional_properties = d
        return baseline_type_3

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
