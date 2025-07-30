from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.engine_config import EngineConfig


T = TypeVar("T", bound="PublishRequest")


@_attrs_define
class PublishRequest:
    """Request to publish a pipeline.

    Attributes:
        model_config_ids (List[int]):
        pipeline_version_id (int):
        engine_config (Union['EngineConfig', None, Unset]):
        replaces (Union[List[int], None, Unset]):
    """

    model_config_ids: List[int]
    pipeline_version_id: int
    engine_config: Union["EngineConfig", None, Unset] = UNSET
    replaces: Union[List[int], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.engine_config import EngineConfig

        model_config_ids = self.model_config_ids

        pipeline_version_id = self.pipeline_version_id

        engine_config: Union[Dict[str, Any], None, Unset]
        if isinstance(self.engine_config, Unset):
            engine_config = UNSET
        elif isinstance(self.engine_config, EngineConfig):
            engine_config = self.engine_config.to_dict()
        else:
            engine_config = self.engine_config

        replaces: Union[List[int], None, Unset]
        if isinstance(self.replaces, Unset):
            replaces = UNSET
        elif isinstance(self.replaces, list):
            replaces = self.replaces

        else:
            replaces = self.replaces

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "model_config_ids": model_config_ids,
                "pipeline_version_id": pipeline_version_id,
            }
        )
        if engine_config is not UNSET:
            field_dict["engine_config"] = engine_config
        if replaces is not UNSET:
            field_dict["replaces"] = replaces

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.engine_config import EngineConfig

        d = src_dict.copy()
        model_config_ids = cast(List[int], d.pop("model_config_ids"))

        pipeline_version_id = d.pop("pipeline_version_id")

        def _parse_engine_config(data: object) -> Union["EngineConfig", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                engine_config_type_1 = EngineConfig.from_dict(data)

                return engine_config_type_1
            except:  # noqa: E722
                pass
            return cast(Union["EngineConfig", None, Unset], data)

        engine_config = _parse_engine_config(d.pop("engine_config", UNSET))

        def _parse_replaces(data: object) -> Union[List[int], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                replaces_type_0 = cast(List[int], data)

                return replaces_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[int], None, Unset], data)

        replaces = _parse_replaces(d.pop("replaces", UNSET))

        publish_request = cls(
            model_config_ids=model_config_ids,
            pipeline_version_id=pipeline_version_id,
            engine_config=engine_config,
            replaces=replaces,
        )

        publish_request.additional_properties = d
        return publish_request

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
