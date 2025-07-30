from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.resources import Resources
    from ..models.sidekick_config import SidekickConfig


T = TypeVar("T", bound="EngineConfig")


@_attrs_define
class EngineConfig:
    """
    Attributes:
        engine (Resources):
        engine_aux (SidekickConfig):
    """

    engine: "Resources"
    engine_aux: "SidekickConfig"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        engine = self.engine.to_dict()

        engine_aux = self.engine_aux.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "engine": engine,
                "engineAux": engine_aux,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.resources import Resources
        from ..models.sidekick_config import SidekickConfig

        d = src_dict.copy()
        engine = Resources.from_dict(d.pop("engine"))

        engine_aux = SidekickConfig.from_dict(d.pop("engineAux"))

        engine_config = cls(
            engine=engine,
            engine_aux=engine_aux,
        )

        engine_config.additional_properties = d
        return engine_config

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
