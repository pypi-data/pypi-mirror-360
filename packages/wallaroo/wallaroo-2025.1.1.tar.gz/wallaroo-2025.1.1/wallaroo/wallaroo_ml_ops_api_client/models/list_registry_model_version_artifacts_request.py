from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="ListRegistryModelVersionArtifactsRequest")


@_attrs_define
class ListRegistryModelVersionArtifactsRequest:
    """Payload for the List Registry Model Version Artifacts call.

    Attributes:
        name (str): The name of the model in the remote Model Registry.
        registry_id (str): The unique identifier of the Model Registry in the Wallaroo system.
        version (str): The version of the model in the remote Model Registry
    """

    name: str
    registry_id: str
    version: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        registry_id = self.registry_id

        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "registry_id": registry_id,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        registry_id = d.pop("registry_id")

        version = d.pop("version")

        list_registry_model_version_artifacts_request = cls(
            name=name,
            registry_id=registry_id,
            version=version,
        )

        list_registry_model_version_artifacts_request.additional_properties = d
        return list_registry_model_version_artifacts_request

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
