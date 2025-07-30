from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.list_models_item import ListModelsItem


T = TypeVar("T", bound="ListModelsResponse")


@_attrs_define
class ListModelsResponse:
    """
    Attributes:
        models (List['ListModelsItem']):
    """

    models: List["ListModelsItem"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        models = []
        for models_item_data in self.models:
            models_item = models_item_data.to_dict()
            models.append(models_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "models": models,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.list_models_item import ListModelsItem

        d = src_dict.copy()
        models = []
        _models = d.pop("models")
        for models_item_data in _models:
            models_item = ListModelsItem.from_dict(models_item_data)

            models.append(models_item)

        list_models_response = cls(
            models=models,
        )

        list_models_response.additional_properties = d
        return list_models_response

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
