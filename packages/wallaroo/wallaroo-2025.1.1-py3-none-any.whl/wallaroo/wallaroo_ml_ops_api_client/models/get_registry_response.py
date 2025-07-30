import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_registry_response_workspace import GetRegistryResponseWorkspace


T = TypeVar("T", bound="GetRegistryResponse")


@_attrs_define
class GetRegistryResponse:
    """Response object for the Get Registry call.

    Attributes:
        created_at (datetime.datetime):
        name (str): A descriptive name for this registry
        token (str): A user token with access to the Registry.
            Tokens must be in base64 format.
        updated_at (datetime.datetime):
        url (str): The URL for accessing this registry
            URLs should allow MLFlow Registry API access
        workspaces (List['GetRegistryResponseWorkspace']):
        id (Union[None, Unset, str]): A unique identifier for this registry
    """

    created_at: datetime.datetime
    name: str
    token: str
    updated_at: datetime.datetime
    url: str
    workspaces: List["GetRegistryResponseWorkspace"]
    id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        created_at = self.created_at.isoformat()

        name = self.name

        token = self.token

        updated_at = self.updated_at.isoformat()

        url = self.url

        workspaces = []
        for workspaces_item_data in self.workspaces:
            workspaces_item = workspaces_item_data.to_dict()
            workspaces.append(workspaces_item)

        id: Union[None, Unset, str]
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "name": name,
                "token": token,
                "updated_at": updated_at,
                "url": url,
                "workspaces": workspaces,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.get_registry_response_workspace import (
            GetRegistryResponseWorkspace,
        )

        d = src_dict.copy()
        created_at = isoparse(d.pop("created_at"))

        name = d.pop("name")

        token = d.pop("token")

        updated_at = isoparse(d.pop("updated_at"))

        url = d.pop("url")

        workspaces = []
        _workspaces = d.pop("workspaces")
        for workspaces_item_data in _workspaces:
            workspaces_item = GetRegistryResponseWorkspace.from_dict(
                workspaces_item_data
            )

            workspaces.append(workspaces_item)

        def _parse_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        id = _parse_id(d.pop("id", UNSET))

        get_registry_response = cls(
            created_at=created_at,
            name=name,
            token=token,
            updated_at=updated_at,
            url=url,
            workspaces=workspaces,
            id=id,
        )

        get_registry_response.additional_properties = d
        return get_registry_response

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
