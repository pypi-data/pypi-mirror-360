from typing import (
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

T = TypeVar("T", bound="DataOrigin")


@_attrs_define
class DataOrigin:
    """Specifies where the data this assay is [Targeting] is coming from.
    Currently, this only refers to which "topic" in Plateau.

        Attributes:
            pipeline_id (int):
            pipeline_name (str):
            workspace_id (int):
            workspace_name (str):
            locations (Union[List[str], None, Unset]): Edge Locations that this assay will include.
                Functionally, this controls which Plateau partitions we include when collecting data for windows.
            model_id (Union[None, Unset, str]): If specified, only runs assays on inferences associated with this Model ID.
                This currently is used to support assays on A/B testing pipelines
                and will be replaced by
    """

    pipeline_id: int
    pipeline_name: str
    workspace_id: int
    workspace_name: str
    locations: Union[List[str], None, Unset] = UNSET
    model_id: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        pipeline_id = self.pipeline_id

        pipeline_name = self.pipeline_name

        workspace_id = self.workspace_id

        workspace_name = self.workspace_name

        locations: Union[List[str], None, Unset]
        if isinstance(self.locations, Unset):
            locations = UNSET
        elif isinstance(self.locations, list):
            locations = self.locations

        else:
            locations = self.locations

        model_id: Union[None, Unset, str]
        if isinstance(self.model_id, Unset):
            model_id = UNSET
        else:
            model_id = self.model_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pipeline_id": pipeline_id,
                "pipeline_name": pipeline_name,
                "workspace_id": workspace_id,
                "workspace_name": workspace_name,
            }
        )
        if locations is not UNSET:
            field_dict["locations"] = locations
        if model_id is not UNSET:
            field_dict["model_id"] = model_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        pipeline_id = d.pop("pipeline_id")

        pipeline_name = d.pop("pipeline_name")

        workspace_id = d.pop("workspace_id")

        workspace_name = d.pop("workspace_name")

        def _parse_locations(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                locations_type_0 = cast(List[str], data)

                return locations_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        locations = _parse_locations(d.pop("locations", UNSET))

        def _parse_model_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        model_id = _parse_model_id(d.pop("model_id", UNSET))

        data_origin = cls(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            locations=locations,
            model_id=model_id,
        )

        data_origin.additional_properties = d
        return data_origin

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
