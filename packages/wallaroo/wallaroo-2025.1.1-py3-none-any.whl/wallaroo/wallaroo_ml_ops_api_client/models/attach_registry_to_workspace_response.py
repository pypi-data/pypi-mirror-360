from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="AttachRegistryToWorkspaceResponse")


@_attrs_define
class AttachRegistryToWorkspaceResponse:
    """
    Attributes:
        id (str): The unique identifier for the Model Registry
        workspace_id (int): The unique identifier for the workspace.
    """

    id: str
    workspace_id: int
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        workspace_id = self.workspace_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "workspace_id": workspace_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        workspace_id = d.pop("workspace_id")

        attach_registry_to_workspace_response = cls(
            id=id,
            workspace_id=workspace_id,
        )

        attach_registry_to_workspace_response.additional_properties = d
        return attach_registry_to_workspace_response

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
