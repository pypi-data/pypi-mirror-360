from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.configured_model_version import ConfiguredModelVersion


T = TypeVar("T", bound="GetModelByIdResponse")


@_attrs_define
class GetModelByIdResponse:
    """
    Attributes:
        model_version (ConfiguredModelVersion):
    """

    model_version: "ConfiguredModelVersion"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        model_version = self.model_version.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_version": model_version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.configured_model_version import ConfiguredModelVersion

        d = src_dict.copy()
        model_version = ConfiguredModelVersion.from_dict(d.pop("model_version"))

        get_model_by_id_response = cls(
            model_version=model_version,
        )

        get_model_by_id_response.additional_properties = d
        return get_model_by_id_response

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
