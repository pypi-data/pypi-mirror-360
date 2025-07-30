from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.rolling_baseline import RollingBaseline


T = TypeVar("T", bound="BaselineType2")


@_attrs_define
class BaselineType2:
    """
    Attributes:
        rolling (RollingBaseline):
    """

    rolling: "RollingBaseline"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        rolling = self.rolling.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Rolling": rolling,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.rolling_baseline import RollingBaseline

        d = src_dict.copy()
        rolling = RollingBaseline.from_dict(d.pop("Rolling"))

        baseline_type_2 = cls(
            rolling=rolling,
        )

        baseline_type_2.additional_properties = d
        return baseline_type_2

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
