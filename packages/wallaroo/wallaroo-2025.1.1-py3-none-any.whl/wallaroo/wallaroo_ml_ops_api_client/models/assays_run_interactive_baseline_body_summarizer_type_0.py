from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..models.assays_run_interactive_baseline_body_summarizer_type_0_aggregation import (
    AssaysRunInteractiveBaselineBodySummarizerType0Aggregation,
)
from ..models.assays_run_interactive_baseline_body_summarizer_type_0_bin_mode import (
    AssaysRunInteractiveBaselineBodySummarizerType0BinMode,
)
from ..models.assays_run_interactive_baseline_body_summarizer_type_0_metric import (
    AssaysRunInteractiveBaselineBodySummarizerType0Metric,
)
from ..models.assays_run_interactive_baseline_body_summarizer_type_0_type import (
    AssaysRunInteractiveBaselineBodySummarizerType0Type,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssaysRunInteractiveBaselineBodySummarizerType0")


@_attrs_define
class AssaysRunInteractiveBaselineBodySummarizerType0:
    """Defines the summarizer/test we want to conduct

    Attributes:
        bin_mode (AssaysRunInteractiveBaselineBodySummarizerType0BinMode):
        aggregation (AssaysRunInteractiveBaselineBodySummarizerType0Aggregation):
        metric (AssaysRunInteractiveBaselineBodySummarizerType0Metric):  How we calculate the score between two
            histograms/vecs.  Add pct_diff and sum_pct_diff?
        num_bins (int):
        type (AssaysRunInteractiveBaselineBodySummarizerType0Type):
        bin_weights (Union[List[float], None, Unset]):
        provided_edges (Union[List[float], None, Unset]):
    """

    bin_mode: AssaysRunInteractiveBaselineBodySummarizerType0BinMode
    aggregation: AssaysRunInteractiveBaselineBodySummarizerType0Aggregation
    metric: AssaysRunInteractiveBaselineBodySummarizerType0Metric
    num_bins: int
    type: AssaysRunInteractiveBaselineBodySummarizerType0Type
    bin_weights: Union[List[float], None, Unset] = UNSET
    provided_edges: Union[List[float], None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        bin_mode = self.bin_mode.value

        aggregation = self.aggregation.value

        metric = self.metric.value

        num_bins = self.num_bins

        type = self.type.value

        bin_weights: Union[List[float], None, Unset]
        if isinstance(self.bin_weights, Unset):
            bin_weights = UNSET
        elif isinstance(self.bin_weights, list):
            bin_weights = self.bin_weights

        else:
            bin_weights = self.bin_weights

        provided_edges: Union[List[float], None, Unset]
        if isinstance(self.provided_edges, Unset):
            provided_edges = UNSET
        elif isinstance(self.provided_edges, list):
            provided_edges = self.provided_edges

        else:
            provided_edges = self.provided_edges

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bin_mode": bin_mode,
                "aggregation": aggregation,
                "metric": metric,
                "num_bins": num_bins,
                "type": type,
            }
        )
        if bin_weights is not UNSET:
            field_dict["bin_weights"] = bin_weights
        if provided_edges is not UNSET:
            field_dict["provided_edges"] = provided_edges

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bin_mode = AssaysRunInteractiveBaselineBodySummarizerType0BinMode(
            d.pop("bin_mode")
        )

        aggregation = AssaysRunInteractiveBaselineBodySummarizerType0Aggregation(
            d.pop("aggregation")
        )

        metric = AssaysRunInteractiveBaselineBodySummarizerType0Metric(d.pop("metric"))

        num_bins = d.pop("num_bins")

        type = AssaysRunInteractiveBaselineBodySummarizerType0Type(d.pop("type"))

        def _parse_bin_weights(data: object) -> Union[List[float], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                bin_weights_type_0 = cast(List[float], data)

                return bin_weights_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[float], None, Unset], data)

        bin_weights = _parse_bin_weights(d.pop("bin_weights", UNSET))

        def _parse_provided_edges(data: object) -> Union[List[float], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                provided_edges_type_0 = cast(List[float], data)

                return provided_edges_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[float], None, Unset], data)

        provided_edges = _parse_provided_edges(d.pop("provided_edges", UNSET))

        assays_run_interactive_baseline_body_summarizer_type_0 = cls(
            bin_mode=bin_mode,
            aggregation=aggregation,
            metric=metric,
            num_bins=num_bins,
            type=type,
            bin_weights=bin_weights,
            provided_edges=provided_edges,
        )

        assays_run_interactive_baseline_body_summarizer_type_0.additional_properties = d
        return assays_run_interactive_baseline_body_summarizer_type_0

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
