import datetime
from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)
from dateutil.parser import isoparse

T = TypeVar("T", bound="Stored")


@_attrs_define
class Stored:
    """
    Attributes:
        stored (List[datetime.datetime]): Use data from the time range specified as the Window.
    """

    stored: List[datetime.datetime]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        stored = []
        for stored_item_data in self.stored:
            stored_item = stored_item_data.isoformat()
            stored.append(stored_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Stored": stored,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        stored = []
        _stored = d.pop("Stored")
        for stored_item_data in _stored:
            stored_item = isoparse(stored_item_data)

            stored.append(stored_item)

        stored = cls(
            stored=stored,
        )

        stored.additional_properties = d
        return stored

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
