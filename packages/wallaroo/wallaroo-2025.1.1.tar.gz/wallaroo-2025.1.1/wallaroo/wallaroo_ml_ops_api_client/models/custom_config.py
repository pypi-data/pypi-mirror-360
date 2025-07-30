from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

T = TypeVar("T", bound="CustomConfig")


@_attrs_define
class CustomConfig:
    """
    Attributes:
        model_path (Union[Unset, str]): The relative path of the model artifacts to the provided zip file. Defaults to
            './model/'. Default: './model/'. Example: ./model/.
    """

    model_path: Union[Unset, str] = "./model/"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        model_path = self.model_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if model_path is not UNSET:
            field_dict["model_path"] = model_path

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        model_path = d.pop("model_path", UNSET)

        custom_config = cls(
            model_path=model_path,
        )

        custom_config.additional_properties = d
        return custom_config

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
