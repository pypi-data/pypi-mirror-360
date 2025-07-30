from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.edge import Edge


T = TypeVar("T", bound="ListEdgesByPublishIdResponse200")


@_attrs_define
class ListEdgesByPublishIdResponse200:
    """Response with a list of edges.

    Attributes:
        edges (List['Edge']): list of edges
    """

    edges: List["Edge"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        edges = []
        for edges_item_data in self.edges:
            edges_item = edges_item_data.to_dict()
            edges.append(edges_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "edges": edges,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.edge import Edge

        d = src_dict.copy()
        edges = []
        _edges = d.pop("edges")
        for edges_item_data in _edges:
            edges_item = Edge.from_dict(edges_item_data)

            edges.append(edges_item)

        list_edges_by_publish_id_response_200 = cls(
            edges=edges,
        )

        list_edges_by_publish_id_response_200.additional_properties = d
        return list_edges_by_publish_id_response_200

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
