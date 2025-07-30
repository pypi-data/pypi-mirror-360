from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.list_all_orchestrations_response_item import (
        ListAllOrchestrationsResponseItem,
    )


T = TypeVar("T", bound="ListAllOrchestrationsResponse")


@_attrs_define
class ListAllOrchestrationsResponse:
    """
    Attributes:
        orchestrations (List['ListAllOrchestrationsResponseItem']):
    """

    orchestrations: List["ListAllOrchestrationsResponseItem"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        orchestrations = []
        for orchestrations_item_data in self.orchestrations:
            orchestrations_item = orchestrations_item_data.to_dict()
            orchestrations.append(orchestrations_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "orchestrations": orchestrations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_all_orchestrations_response_item import (
            ListAllOrchestrationsResponseItem,
        )

        d = src_dict.copy()
        orchestrations = []
        _orchestrations = d.pop("orchestrations")
        for orchestrations_item_data in _orchestrations:
            orchestrations_item = ListAllOrchestrationsResponseItem.from_dict(
                orchestrations_item_data
            )

            orchestrations.append(orchestrations_item)

        list_all_orchestrations_response = cls(
            orchestrations=orchestrations,
        )

        list_all_orchestrations_response.additional_properties = d
        return list_all_orchestrations_response

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
