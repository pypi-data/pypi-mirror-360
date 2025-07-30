from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

T = TypeVar("T", bound="DeleteOrchestrationsBody")


@_attrs_define
class DeleteOrchestrationsBody:
    """Deletes the specified orchestrations.

    Attributes:
        orchestrations (List[str]): Orchestration IDs
        confirm_delete (Union[Unset, bool]): Confirm delete
    """

    orchestrations: List[str]
    confirm_delete: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        orchestrations = self.orchestrations

        confirm_delete = self.confirm_delete

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "orchestrations": orchestrations,
            }
        )
        if confirm_delete is not UNSET:
            field_dict["confirm_delete"] = confirm_delete

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        orchestrations = cast(List[str], d.pop("orchestrations"))

        confirm_delete = d.pop("confirm_delete", UNSET)

        delete_orchestrations_body = cls(
            orchestrations=orchestrations,
            confirm_delete=confirm_delete,
        )

        delete_orchestrations_body.additional_properties = d
        return delete_orchestrations_body

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
