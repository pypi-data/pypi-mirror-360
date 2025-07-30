from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_version_stub import ModelVersionStub


T = TypeVar("T", bound="DeployPipelineRequest")


@_attrs_define
class DeployPipelineRequest:
    """Pipeline deployment request.

    Attributes:
        deploy_id (str): Deployment identifier.
        engine_config (Union[Unset, Any]): Optional engine configuration.
        model_configs (Union[List[int], None, Unset]): Optional model configurations.
        model_ids (Union[List[int], None, Unset]): Optional model identifiers.
            If model_ids are passed in, we will create model_configs for them.
        models (Union[List['ModelVersionStub'], None, Unset]): Optional model.
            Because model_ids may not be readily available for existing pipelines, they can pass in all the data again.
        pipeline_id (Union[None, Unset, int]): Pipeline identifier.
        pipeline_version (Union[None, Unset, str]): Optional pipeline version identifier.
        pipeline_version_pk_id (Union[None, Unset, int]): Internal pipeline version identifier.
    """

    deploy_id: str
    engine_config: Union[Unset, Any] = UNSET
    model_configs: Union[List[int], None, Unset] = UNSET
    model_ids: Union[List[int], None, Unset] = UNSET
    models: Union[List["ModelVersionStub"], None, Unset] = UNSET
    pipeline_id: Union[None, Unset, int] = UNSET
    pipeline_version: Union[None, Unset, str] = UNSET
    pipeline_version_pk_id: Union[None, Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        deploy_id = self.deploy_id

        engine_config = self.engine_config

        model_configs: Union[List[int], None, Unset]
        if isinstance(self.model_configs, Unset):
            model_configs = UNSET
        elif isinstance(self.model_configs, list):
            model_configs = self.model_configs

        else:
            model_configs = self.model_configs

        model_ids: Union[List[int], None, Unset]
        if isinstance(self.model_ids, Unset):
            model_ids = UNSET
        elif isinstance(self.model_ids, list):
            model_ids = self.model_ids

        else:
            model_ids = self.model_ids

        models: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.models, Unset):
            models = UNSET
        elif isinstance(self.models, list):
            models = []
            for models_type_0_item_data in self.models:
                models_type_0_item = models_type_0_item_data.to_dict()
                models.append(models_type_0_item)

        else:
            models = self.models

        pipeline_id: Union[None, Unset, int]
        if isinstance(self.pipeline_id, Unset):
            pipeline_id = UNSET
        else:
            pipeline_id = self.pipeline_id

        pipeline_version: Union[None, Unset, str]
        if isinstance(self.pipeline_version, Unset):
            pipeline_version = UNSET
        else:
            pipeline_version = self.pipeline_version

        pipeline_version_pk_id: Union[None, Unset, int]
        if isinstance(self.pipeline_version_pk_id, Unset):
            pipeline_version_pk_id = UNSET
        else:
            pipeline_version_pk_id = self.pipeline_version_pk_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deploy_id": deploy_id,
            }
        )
        if engine_config is not UNSET:
            field_dict["engine_config"] = engine_config
        if model_configs is not UNSET:
            field_dict["model_configs"] = model_configs
        if model_ids is not UNSET:
            field_dict["model_ids"] = model_ids
        if models is not UNSET:
            field_dict["models"] = models
        if pipeline_id is not UNSET:
            field_dict["pipeline_id"] = pipeline_id
        if pipeline_version is not UNSET:
            field_dict["pipeline_version"] = pipeline_version
        if pipeline_version_pk_id is not UNSET:
            field_dict["pipeline_version_pk_id"] = pipeline_version_pk_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.model_version_stub import ModelVersionStub

        d = src_dict.copy()
        deploy_id = d.pop("deploy_id")

        engine_config = d.pop("engine_config", UNSET)

        def _parse_model_configs(data: object) -> Union[List[int], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                model_configs_type_0 = cast(List[int], data)

                return model_configs_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[int], None, Unset], data)

        model_configs = _parse_model_configs(d.pop("model_configs", UNSET))

        def _parse_model_ids(data: object) -> Union[List[int], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                model_ids_type_0 = cast(List[int], data)

                return model_ids_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[int], None, Unset], data)

        model_ids = _parse_model_ids(d.pop("model_ids", UNSET))

        def _parse_models(data: object) -> Union[List["ModelVersionStub"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                models_type_0 = []
                _models_type_0 = data
                for models_type_0_item_data in _models_type_0:
                    models_type_0_item = ModelVersionStub.from_dict(
                        models_type_0_item_data
                    )

                    models_type_0.append(models_type_0_item)

                return models_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["ModelVersionStub"], None, Unset], data)

        models = _parse_models(d.pop("models", UNSET))

        def _parse_pipeline_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        pipeline_id = _parse_pipeline_id(d.pop("pipeline_id", UNSET))

        def _parse_pipeline_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        pipeline_version = _parse_pipeline_version(d.pop("pipeline_version", UNSET))

        def _parse_pipeline_version_pk_id(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        pipeline_version_pk_id = _parse_pipeline_version_pk_id(
            d.pop("pipeline_version_pk_id", UNSET)
        )

        deploy_pipeline_request = cls(
            deploy_id=deploy_id,
            engine_config=engine_config,
            model_configs=model_configs,
            model_ids=model_ids,
            models=models,
            pipeline_id=pipeline_id,
            pipeline_version=pipeline_version,
            pipeline_version_pk_id=pipeline_version_pk_id,
        )

        deploy_pipeline_request.additional_properties = d
        return deploy_pipeline_request

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
