from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType0")


@_attrs_define
class AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType0:
    """
    Attributes:
        vector (List[float]):
    """

    vector: List[float]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        vector = self.vector

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "vector": vector,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        vector = cast(List[float], d.pop("vector"))

        assays_run_interactive_baseline_body_baseline_type_0_calculated_type_0 = cls(
            vector=vector,
        )

        assays_run_interactive_baseline_body_baseline_type_0_calculated_type_0.additional_properties = d
        return assays_run_interactive_baseline_body_baseline_type_0_calculated_type_0

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
