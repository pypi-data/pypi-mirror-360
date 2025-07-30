from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="BinModeType4")


@_attrs_define
class BinModeType4:
    """
    Attributes:
        provided (List[float]): A Vec of the right-edges of a set of histogram bins.
            The right-edge may be [`std::f64::INFINITY`]
    """

    provided: List[float]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        provided = self.provided

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Provided": provided,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        provided = cast(List[float], d.pop("Provided"))

        bin_mode_type_4 = cls(
            provided=provided,
        )

        bin_mode_type_4.additional_properties = d
        return bin_mode_type_4

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
