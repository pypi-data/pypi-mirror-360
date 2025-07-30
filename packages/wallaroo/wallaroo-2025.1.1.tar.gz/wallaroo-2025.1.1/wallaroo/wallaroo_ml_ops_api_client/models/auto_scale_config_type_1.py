from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.auto_scale_config_type_1_type import AutoScaleConfigType1Type

T = TypeVar("T", bound="AutoScaleConfigType1")


@_attrs_define
class AutoScaleConfigType1:
    """
    Attributes:
        replica_max (int):
        replica_min (int):
        type (AutoScaleConfigType1Type):
    """

    replica_max: int
    replica_min: int
    type: AutoScaleConfigType1Type
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        replica_max = self.replica_max

        replica_min = self.replica_min

        type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "replica_max": replica_max,
                "replica_min": replica_min,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        replica_max = d.pop("replica_max")

        replica_min = d.pop("replica_min")

        type = AutoScaleConfigType1Type(d.pop("type"))

        auto_scale_config_type_1 = cls(
            replica_max=replica_max,
            replica_min=replica_min,
            type=type,
        )

        auto_scale_config_type_1.additional_properties = d
        return auto_scale_config_type_1

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
