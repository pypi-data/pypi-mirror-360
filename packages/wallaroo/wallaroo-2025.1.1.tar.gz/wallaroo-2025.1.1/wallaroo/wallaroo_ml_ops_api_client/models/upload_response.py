from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.insert_models import InsertModels


T = TypeVar("T", bound="UploadResponse")


@_attrs_define
class UploadResponse:
    """
    Attributes:
        insert_models (InsertModels):
    """

    insert_models: "InsertModels"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        insert_models = self.insert_models.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "insert_models": insert_models,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.insert_models import InsertModels

        d = src_dict.copy()
        insert_models = InsertModels.from_dict(d.pop("insert_models"))

        upload_response = cls(
            insert_models=insert_models,
        )

        upload_response.additional_properties = d
        return upload_response

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
