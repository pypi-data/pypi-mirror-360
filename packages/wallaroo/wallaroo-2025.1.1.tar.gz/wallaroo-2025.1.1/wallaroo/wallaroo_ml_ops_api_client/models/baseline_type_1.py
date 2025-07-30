import datetime
from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)
from dateutil.parser import isoparse

T = TypeVar("T", bound="BaselineType1")


@_attrs_define
class BaselineType1:
    """
    Attributes:
        static (List[datetime.datetime]): Use a static timeframe as a Baseline.
            This gets stored as a computed summary under the hood,
            so it's only used during Baseline Preview or Assay Creation.
    """

    static: List[datetime.datetime]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        static = []
        for static_item_data in self.static:
            static_item = static_item_data.isoformat()
            static.append(static_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Static": static,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        static = []
        _static = d.pop("Static")
        for static_item_data in _static:
            static_item = isoparse(static_item_data)

            static.append(static_item)

        baseline_type_1 = cls(
            static=static,
        )

        baseline_type_1.additional_properties = d
        return baseline_type_1

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
