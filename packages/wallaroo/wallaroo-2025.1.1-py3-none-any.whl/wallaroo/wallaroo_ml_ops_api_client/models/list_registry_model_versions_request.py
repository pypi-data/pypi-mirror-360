from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="ListRegistryModelVersionsRequest")


@_attrs_define
class ListRegistryModelVersionsRequest:
    """Payload for the List Registry Models call.

    Attributes:
        model_name (str):
        registry_id (str):
    """

    model_name: str
    registry_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        model_name = self.model_name

        registry_id = self.registry_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_name": model_name,
                "registry_id": registry_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        model_name = d.pop("model_name")

        registry_id = d.pop("registry_id")

        list_registry_model_versions_request = cls(
            model_name=model_name,
            registry_id=registry_id,
        )

        list_registry_model_versions_request.additional_properties = d
        return list_registry_model_versions_request

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
