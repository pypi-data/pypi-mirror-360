from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="WorkspacesListResponse200WorkspacesItem")


@_attrs_define
class WorkspacesListResponse200WorkspacesItem:
    """Data returned from listing Workspaces

    Attributes:
        id (int):  Workspace numeric ID
        name (str):  Descriptive name
        created_at (str):  Created At timestamp
        created_by (str):  UUID identifier for the User that created this Workspace
        archived (bool):  If this Workspace has been archived
        models (List[int]):  List of Model IDs present in Workspace
        pipelines (List[int]):  List of Pipeline IDs present in Workspace
    """

    id: int
    name: str
    created_at: str
    created_by: str
    archived: bool
    models: List[int]
    pipelines: List[int]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        created_at = self.created_at

        created_by = self.created_by

        archived = self.archived

        models = self.models

        pipelines = self.pipelines

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "created_at": created_at,
                "created_by": created_by,
                "archived": archived,
                "models": models,
                "pipelines": pipelines,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        created_at = d.pop("created_at")

        created_by = d.pop("created_by")

        archived = d.pop("archived")

        models = cast(List[int], d.pop("models"))

        pipelines = cast(List[int], d.pop("pipelines"))

        workspaces_list_response_200_workspaces_item = cls(
            id=id,
            name=name,
            created_at=created_at,
            created_by=created_by,
            archived=archived,
            models=models,
            pipelines=pipelines,
        )

        workspaces_list_response_200_workspaces_item.additional_properties = d
        return workspaces_list_response_200_workspaces_item

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
