import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.window_width_duration import WindowWidthDuration


T = TypeVar("T", bound="RollingBaseline")


@_attrs_define
class RollingBaseline:
    """
    Attributes:
        start (datetime.datetime):
        width (WindowWidthDuration):
    """

    start: datetime.datetime
    width: "WindowWidthDuration"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        start = self.start.isoformat()

        width = self.width.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "start": start,
                "width": width,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.window_width_duration import WindowWidthDuration

        d = src_dict.copy()
        start = isoparse(d.pop("start"))

        width = WindowWidthDuration.from_dict(d.pop("width"))

        rolling_baseline = cls(
            start=start,
            width=width,
        )

        rolling_baseline.additional_properties = d
        return rolling_baseline

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
