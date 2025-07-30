from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.model_config import ModelConfig


T = TypeVar("T", bound="InsertModelConfigResponse")


@_attrs_define
class InsertModelConfigResponse:
    """
    Attributes:
        model_config (ModelConfig): Wrapper struct to add a realized database ID to an underlying data struct.
    """

    model_config: "ModelConfig"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        model_config = self.model_config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_config": model_config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.model_config import ModelConfig

        d = src_dict.copy()
        model_config = ModelConfig.from_dict(d.pop("model_config"))

        insert_model_config_response = cls(
            model_config=model_config,
        )

        insert_model_config_response.additional_properties = d
        return insert_model_config_response

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
