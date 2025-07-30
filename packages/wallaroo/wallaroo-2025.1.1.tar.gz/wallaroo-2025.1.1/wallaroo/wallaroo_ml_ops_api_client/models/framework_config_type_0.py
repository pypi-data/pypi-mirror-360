from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.framework_config_type_0_framework import FrameworkConfigType0Framework

if TYPE_CHECKING:
    from ..models.vllm_config import VLLMConfig


T = TypeVar("T", bound="FrameworkConfigType0")


@_attrs_define
class FrameworkConfigType0:
    """
    Attributes:
        config (VLLMConfig):
        framework (FrameworkConfigType0Framework):
    """

    config: "VLLMConfig"
    framework: FrameworkConfigType0Framework
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        config = self.config.to_dict()

        framework = self.framework.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
                "framework": framework,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.vllm_config import VLLMConfig

        d = src_dict.copy()
        config = VLLMConfig.from_dict(d.pop("config"))

        framework = FrameworkConfigType0Framework(d.pop("framework"))

        framework_config_type_0 = cls(
            config=config,
            framework=framework,
        )

        framework_config_type_0.additional_properties = d
        return framework_config_type_0

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
