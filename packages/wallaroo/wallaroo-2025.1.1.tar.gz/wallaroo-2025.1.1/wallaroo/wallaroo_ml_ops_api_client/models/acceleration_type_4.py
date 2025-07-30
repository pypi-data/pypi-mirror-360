from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.qaic_config import QaicConfig


T = TypeVar("T", bound="AccelerationType4")


@_attrs_define
class AccelerationType4:
    """
    Attributes:
        qaic (QaicConfig):
    """

    qaic: "QaicConfig"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        qaic = self.qaic.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "qaic": qaic,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.qaic_config import QaicConfig

        d = src_dict.copy()
        qaic = QaicConfig.from_dict(d.pop("qaic"))

        acceleration_type_4 = cls(
            qaic=qaic,
        )

        acceleration_type_4.additional_properties = d
        return acceleration_type_4

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
