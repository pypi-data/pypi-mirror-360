from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.status_get_deployment_response_200_status import (
    StatusGetDeploymentResponse200Status,
)

if TYPE_CHECKING:
    from ..models.status_get_deployment_response_200_engine_lbs_item import (
        StatusGetDeploymentResponse200EngineLbsItem,
    )
    from ..models.status_get_deployment_response_200_engines_item import (
        StatusGetDeploymentResponse200EnginesItem,
    )
    from ..models.status_get_deployment_response_200_helm_item import (
        StatusGetDeploymentResponse200HelmItem,
    )
    from ..models.status_get_deployment_response_200_sidekicks_item import (
        StatusGetDeploymentResponse200SidekicksItem,
    )


T = TypeVar("T", bound="StatusGetDeploymentResponse200")


@_attrs_define
class StatusGetDeploymentResponse200:
    """Pipeline deployment status.

    Attributes:
        status (StatusGetDeploymentResponse200Status):  Current status of deployment.
        details (List[str]):  Deployment status details.
        engines (List['StatusGetDeploymentResponse200EnginesItem']):  Engine statuses.
        engine_lbs (List['StatusGetDeploymentResponse200EngineLbsItem']):  Load balancer statuses.
        sidekicks (List['StatusGetDeploymentResponse200SidekicksItem']):  Sidekick container statuses.
        helm (List['StatusGetDeploymentResponse200HelmItem']):
    """

    status: StatusGetDeploymentResponse200Status
    details: List[str]
    engines: List["StatusGetDeploymentResponse200EnginesItem"]
    engine_lbs: List["StatusGetDeploymentResponse200EngineLbsItem"]
    sidekicks: List["StatusGetDeploymentResponse200SidekicksItem"]
    helm: List["StatusGetDeploymentResponse200HelmItem"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status = self.status.value

        details = self.details

        engines = []
        for engines_item_data in self.engines:
            engines_item = engines_item_data.to_dict()
            engines.append(engines_item)

        engine_lbs = []
        for engine_lbs_item_data in self.engine_lbs:
            engine_lbs_item = engine_lbs_item_data.to_dict()
            engine_lbs.append(engine_lbs_item)

        sidekicks = []
        for sidekicks_item_data in self.sidekicks:
            sidekicks_item = sidekicks_item_data.to_dict()
            sidekicks.append(sidekicks_item)

        helm = []
        for helm_item_data in self.helm:
            helm_item = helm_item_data.to_dict()
            helm.append(helm_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "details": details,
                "engines": engines,
                "engine_lbs": engine_lbs,
                "sidekicks": sidekicks,
                "helm": helm,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.status_get_deployment_response_200_engine_lbs_item import (
            StatusGetDeploymentResponse200EngineLbsItem,
        )
        from ..models.status_get_deployment_response_200_engines_item import (
            StatusGetDeploymentResponse200EnginesItem,
        )
        from ..models.status_get_deployment_response_200_helm_item import (
            StatusGetDeploymentResponse200HelmItem,
        )
        from ..models.status_get_deployment_response_200_sidekicks_item import (
            StatusGetDeploymentResponse200SidekicksItem,
        )

        d = src_dict.copy()
        status = StatusGetDeploymentResponse200Status(d.pop("status"))

        details = cast(List[str], d.pop("details"))

        engines = []
        _engines = d.pop("engines")
        for engines_item_data in _engines:
            engines_item = StatusGetDeploymentResponse200EnginesItem.from_dict(
                engines_item_data
            )

            engines.append(engines_item)

        engine_lbs = []
        _engine_lbs = d.pop("engine_lbs")
        for engine_lbs_item_data in _engine_lbs:
            engine_lbs_item = StatusGetDeploymentResponse200EngineLbsItem.from_dict(
                engine_lbs_item_data
            )

            engine_lbs.append(engine_lbs_item)

        sidekicks = []
        _sidekicks = d.pop("sidekicks")
        for sidekicks_item_data in _sidekicks:
            sidekicks_item = StatusGetDeploymentResponse200SidekicksItem.from_dict(
                sidekicks_item_data
            )

            sidekicks.append(sidekicks_item)

        helm = []
        _helm = d.pop("helm")
        for helm_item_data in _helm:
            helm_item = StatusGetDeploymentResponse200HelmItem.from_dict(helm_item_data)

            helm.append(helm_item)

        status_get_deployment_response_200 = cls(
            status=status,
            details=details,
            engines=engines,
            engine_lbs=engine_lbs,
            sidekicks=sidekicks,
            helm=helm,
        )

        status_get_deployment_response_200.additional_properties = d
        return status_get_deployment_response_200

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
