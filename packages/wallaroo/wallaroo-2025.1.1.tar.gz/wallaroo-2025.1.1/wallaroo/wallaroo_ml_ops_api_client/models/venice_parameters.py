from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="VeniceParameters")


@_attrs_define
class VeniceParameters:
    """
    Attributes:
        include_venice_system_prompt (bool):
    """

    include_venice_system_prompt: bool
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        include_venice_system_prompt = self.include_venice_system_prompt

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "include_venice_system_prompt": include_venice_system_prompt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        include_venice_system_prompt = d.pop("include_venice_system_prompt")

        venice_parameters = cls(
            include_venice_system_prompt=include_venice_system_prompt,
        )

        venice_parameters.additional_properties = d
        return venice_parameters

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
