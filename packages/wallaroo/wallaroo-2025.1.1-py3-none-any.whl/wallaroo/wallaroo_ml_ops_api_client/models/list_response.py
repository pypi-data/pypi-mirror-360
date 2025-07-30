from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.edge import Edge
    from ..models.pipeline_publish import PipelinePublish


T = TypeVar("T", bound="ListResponse")


@_attrs_define
class ListResponse:
    """Response with a list of published pipelines.

    Attributes:
        edges (List['Edge']): list of edges for the pipeline
        publishes (List['PipelinePublish']): list of published pipelines
    """

    edges: List["Edge"]
    publishes: List["PipelinePublish"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        edges = []
        for edges_item_data in self.edges:
            edges_item = edges_item_data.to_dict()
            edges.append(edges_item)

        publishes = []
        for publishes_item_data in self.publishes:
            publishes_item = publishes_item_data.to_dict()
            publishes.append(publishes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "edges": edges,
                "publishes": publishes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.edge import Edge
        from ..models.pipeline_publish import PipelinePublish

        d = src_dict.copy()
        edges = []
        _edges = d.pop("edges")
        for edges_item_data in _edges:
            edges_item = Edge.from_dict(edges_item_data)

            edges.append(edges_item)

        publishes = []
        _publishes = d.pop("publishes")
        for publishes_item_data in _publishes:
            publishes_item = PipelinePublish.from_dict(publishes_item_data)

            publishes.append(publishes_item)

        list_response = cls(
            edges=edges,
            publishes=publishes,
        )

        list_response.additional_properties = d
        return list_response

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
