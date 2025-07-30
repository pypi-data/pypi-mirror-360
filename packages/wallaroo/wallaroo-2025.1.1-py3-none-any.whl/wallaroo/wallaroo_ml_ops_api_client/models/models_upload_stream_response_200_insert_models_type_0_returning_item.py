from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.models_upload_stream_response_200_insert_models_type_0_returning_item_models_item import (
        ModelsUploadStreamResponse200InsertModelsType0ReturningItemModelsItem,
    )


T = TypeVar("T", bound="ModelsUploadStreamResponse200InsertModelsType0ReturningItem")


@_attrs_define
class ModelsUploadStreamResponse200InsertModelsType0ReturningItem:
    """Upload model response detail.

    Attributes:
        models (List['ModelsUploadStreamResponse200InsertModelsType0ReturningItemModelsItem']):  List of uploaded
            models.
    """

    models: List[
        "ModelsUploadStreamResponse200InsertModelsType0ReturningItemModelsItem"
    ]
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
        from ..models.models_upload_stream_response_200_insert_models_type_0_returning_item_models_item import (
            ModelsUploadStreamResponse200InsertModelsType0ReturningItemModelsItem,
        )

        d = src_dict.copy()
        models = []
        _models = d.pop("models")
        for models_item_data in _models:
            models_item = ModelsUploadStreamResponse200InsertModelsType0ReturningItemModelsItem.from_dict(
                models_item_data
            )

            models.append(models_item)

        models_upload_stream_response_200_insert_models_type_0_returning_item = cls(
            models=models,
        )

        models_upload_stream_response_200_insert_models_type_0_returning_item.additional_properties = d
        return models_upload_stream_response_200_insert_models_type_0_returning_item

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
