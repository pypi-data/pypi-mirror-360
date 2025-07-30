from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetTaskByIdRequest")


@_attrs_define
class GetTaskByIdRequest:
    """
    Attributes:
        id (str):
        run_limit (Union[None, Unset, int]):
    """

    id: str
    run_limit: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        run_limit: Union[None, Unset, int]
        if isinstance(self.run_limit, Unset):
            run_limit = UNSET
        else:
            run_limit = self.run_limit

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if run_limit is not UNSET:
            field_dict["run_limit"] = run_limit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        def _parse_run_limit(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        run_limit = _parse_run_limit(d.pop("run_limit", UNSET))

        get_task_by_id_request = cls(
            id=id,
            run_limit=run_limit,
        )

        get_task_by_id_request.additional_properties = d
        return get_task_by_id_request

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
