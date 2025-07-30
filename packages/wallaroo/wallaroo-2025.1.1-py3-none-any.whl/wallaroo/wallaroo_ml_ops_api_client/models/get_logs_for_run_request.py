from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetLogsForRunRequest")


@_attrs_define
class GetLogsForRunRequest:
    """
    Attributes:
        id (str):
        lines (Union[None, Unset, int]):
    """

    id: str
    lines: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        lines: Union[None, Unset, int]
        if isinstance(self.lines, Unset):
            lines = UNSET
        else:
            lines = self.lines

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if lines is not UNSET:
            field_dict["lines"] = lines

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        def _parse_lines(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        lines = _parse_lines(d.pop("lines", UNSET))

        get_logs_for_run_request = cls(
            id=id,
            lines=lines,
        )

        get_logs_for_run_request.additional_properties = d
        return get_logs_for_run_request

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
