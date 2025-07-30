from typing import Any, Dict, List, Type, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

T = TypeVar("T", bound="DeletePipelineVersionsRequest")


@_attrs_define
class DeletePipelineVersionsRequest:
    """Request to list published pipelines.

    Attributes:
        pipeline_versions (List[str]): Pipeline ID
    """

    pipeline_versions: List[str]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pipeline_versions = self.pipeline_versions

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pipeline_versions": pipeline_versions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pipeline_versions = cast(List[str], d.pop("pipeline_versions"))

        delete_pipeline_versions_request = cls(
            pipeline_versions=pipeline_versions,
        )

        delete_pipeline_versions_request.additional_properties = d
        return delete_pipeline_versions_request

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
