from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="GetLogsForRunResponse200")


@_attrs_define
class GetLogsForRunResponse200:
    """
    Attributes:
        logs (List[str]):
    """

    logs: List[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        logs = self.logs

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "logs": logs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        logs = cast(List[str], d.pop("logs"))

        get_logs_for_run_response_200 = cls(
            logs=logs,
        )

        get_logs_for_run_response_200.additional_properties = d
        return get_logs_for_run_response_200

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
