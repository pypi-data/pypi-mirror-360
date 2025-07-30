import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)
from dateutil.parser import isoparse

from ..models.app_version import AppVersion
from ..models.orchestration_status import OrchestrationStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="Orchestration")


@_attrs_define
class Orchestration:
    """A struct that mirrors the data in Hasura's Orchestration table.

    Attributes:
        created_at (datetime.datetime): When this [Orchestration] was first inserted into the db.
            Optional because they are read-only
        file_name (str): The name of the ZIP archive uploaded by the user. This may be user-provided.
        file_size (int): The file size of the orchestration file
        id (str): The unique identifier for the [Orchestration].
        image_path (str): Image path for orchestration deployment
            This pins the orchestration to a specific image, mostly for version control
        owner_id (str): This is the UserID of the end user that initiated the upload of this [Orchestration]
        sha (str): The sha256 [String] of the user's uploaded ZIP file.
        status (OrchestrationStatus): The possible states an [Orchestration]'s Packaging status can be in.
        updated_at (datetime.datetime): When this [Orchestration] was last updated in the db.
            Optional because they are read-only
        workspace_id (int): The numeric identifier of the Workspace.
        created_by (Union[None, Unset, str]): The user who created the orchestration
        created_on_version (Union[Unset, AppVersion]):
        name (Union[None, Unset, str]): An optional descriptive name provided by the user.
        task_id (Union[None, Unset, int, str]):
    """

    created_at: datetime.datetime
    file_name: str
    file_size: int
    id: str
    image_path: str
    owner_id: str
    sha: str
    status: OrchestrationStatus
    updated_at: datetime.datetime
    workspace_id: int
    created_by: Union[None, Unset, str] = UNSET
    created_on_version: Union[Unset, AppVersion] = UNSET
    name: Union[None, Unset, str] = UNSET
    task_id: Union[None, Unset, int, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()

        file_name = self.file_name

        file_size = self.file_size

        id = self.id

        image_path = self.image_path

        owner_id = self.owner_id

        sha = self.sha

        status = self.status.value

        updated_at = self.updated_at.isoformat()

        workspace_id = self.workspace_id

        created_by: Union[None, Unset, str]
        if isinstance(self.created_by, Unset):
            created_by = UNSET
        else:
            created_by = self.created_by

        created_on_version: Union[Unset, str] = UNSET
        if not isinstance(self.created_on_version, Unset):
            created_on_version = self.created_on_version.value

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        task_id: Union[None, Unset, int, str]
        if isinstance(self.task_id, Unset):
            task_id = UNSET
        else:
            task_id = self.task_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "file_name": file_name,
                "file_size": file_size,
                "id": id,
                "image_path": image_path,
                "owner_id": owner_id,
                "sha": sha,
                "status": status,
                "updated_at": updated_at,
                "workspace_id": workspace_id,
            }
        )
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if created_on_version is not UNSET:
            field_dict["created_on_version"] = created_on_version
        if name is not UNSET:
            field_dict["name"] = name
        if task_id is not UNSET:
            field_dict["task_id"] = task_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        file_name = d.pop("file_name")

        file_size = d.pop("file_size")

        id = d.pop("id")

        image_path = d.pop("image_path")

        owner_id = d.pop("owner_id")

        sha = d.pop("sha")

        status = OrchestrationStatus(d.pop("status"))

        updated_at = isoparse(d.pop("updated_at"))

        workspace_id = d.pop("workspace_id")

        def _parse_created_by(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        created_by = _parse_created_by(d.pop("created_by", UNSET))

        _created_on_version = d.pop("created_on_version", UNSET)
        created_on_version: Union[Unset, AppVersion]
        if isinstance(_created_on_version, Unset):
            created_on_version = UNSET
        else:
            created_on_version = AppVersion(_created_on_version)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_task_id(data: object) -> Union[None, Unset, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int, str], data)

        task_id = _parse_task_id(d.pop("task_id", UNSET))

        orchestration = cls(
            created_at=created_at,
            file_name=file_name,
            file_size=file_size,
            id=id,
            image_path=image_path,
            owner_id=owner_id,
            sha=sha,
            status=status,
            updated_at=updated_at,
            workspace_id=workspace_id,
            created_by=created_by,
            created_on_version=created_on_version,
            name=name,
            task_id=task_id,
        )

        orchestration.additional_properties = d
        return orchestration

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
