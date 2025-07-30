from typing import Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.assays_get_assay_by_id_response_200_summarizer_type_1_type import (
    AssaysGetAssayByIdResponse200SummarizerType1Type,
)

T = TypeVar("T", bound="AssaysGetAssayByIdResponse200SummarizerType1")


@_attrs_define
class AssaysGetAssayByIdResponse200SummarizerType1:
    """
    Attributes:
        name (str):
        type (AssaysGetAssayByIdResponse200SummarizerType1Type):
    """

    name: str
    type: AssaysGetAssayByIdResponse200SummarizerType1Type
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        type = AssaysGetAssayByIdResponse200SummarizerType1Type(d.pop("type"))

        assays_get_assay_by_id_response_200_summarizer_type_1 = cls(
            name=name,
            type=type,
        )

        assays_get_assay_by_id_response_200_summarizer_type_1.additional_properties = d
        return assays_get_assay_by_id_response_200_summarizer_type_1

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
