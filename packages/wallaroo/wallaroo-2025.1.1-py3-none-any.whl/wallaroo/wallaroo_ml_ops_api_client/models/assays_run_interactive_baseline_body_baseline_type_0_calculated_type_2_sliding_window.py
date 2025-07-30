from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

if TYPE_CHECKING:
    from ..models.assays_run_interactive_baseline_body_baseline_type_0_calculated_type_2_sliding_window_window import (
        AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType2SlidingWindowWindow,
    )


T = TypeVar(
    "T",
    bound="AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType2SlidingWindow",
)


@_attrs_define
class AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType2SlidingWindow:
    """
    Attributes:
        window (AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType2SlidingWindowWindow):  Assay window.
        offset (str):
    """

    window: "AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType2SlidingWindowWindow"
    offset: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        window = self.window.to_dict()

        offset = self.offset

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "window": window,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.assays_run_interactive_baseline_body_baseline_type_0_calculated_type_2_sliding_window_window import (
            AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType2SlidingWindowWindow,
        )

        d = src_dict.copy()
        window = AssaysRunInteractiveBaselineBodyBaselineType0CalculatedType2SlidingWindowWindow.from_dict(
            d.pop("window")
        )

        offset = d.pop("offset")

        assays_run_interactive_baseline_body_baseline_type_0_calculated_type_2_sliding_window = cls(
            window=window,
            offset=offset,
        )

        assays_run_interactive_baseline_body_baseline_type_0_calculated_type_2_sliding_window.additional_properties = d
        return assays_run_interactive_baseline_body_baseline_type_0_calculated_type_2_sliding_window

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
