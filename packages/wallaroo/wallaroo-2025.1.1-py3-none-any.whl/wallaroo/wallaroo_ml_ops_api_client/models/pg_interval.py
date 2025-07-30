from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.interval_unit import IntervalUnit

T = TypeVar("T", bound="PGInterval")


@_attrs_define
class PGInterval:
    """A struct that allows you to specify "Run every 3 days", where days is the `interval` [IntervalUnit] and 3 is the
    `skip`.
    This is used by Postgres (via init_assay_result.rs) to compute the next Start Time.

        Attributes:
            quantity (int): The Quantity portion of Postgres's INTERVAL type
            unit (IntervalUnit): See <https://www.postgresql.org/docs/current/datatype-datetime.html#DATATYPE-INTERVAL-
                INPUT>
    """

    quantity: int
    unit: IntervalUnit
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        quantity = self.quantity

        unit = self.unit.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "quantity": quantity,
                "unit": unit,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        quantity = d.pop("quantity")

        unit = IntervalUnit(d.pop("unit"))

        pg_interval = cls(
            quantity=quantity,
            unit=unit,
        )

        pg_interval.additional_properties = d
        return pg_interval

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
