from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.thresholds import Thresholds


T = TypeVar("T", bound="DataPath")


@_attrs_define
class DataPath:
    """Flexible way of designating what the assay is monitoring

    Attributes:
        field (str): A name that can be used by [`polars::prelude::Field`] to extract a column of data from the
            inference records.
            If the Named Field is not a [`polars::prelude::DataType::List`], the index is ignored.
        indexes (Union[List[int], None, Unset]): The indexes of the field to monitor, if a list.
            If this is a scalar value instead, either pass an empty array or no array at all.
            Structs are not currently supported.
        thresholds (Union['Thresholds', None, Unset]):
    """

    field: str
    indexes: Union[List[int], None, Unset] = UNSET
    thresholds: Union["Thresholds", None, Unset] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.thresholds import Thresholds

        field = self.field

        indexes: Union[List[int], None, Unset]
        if isinstance(self.indexes, Unset):
            indexes = UNSET
        elif isinstance(self.indexes, list):
            indexes = self.indexes

        else:
            indexes = self.indexes

        thresholds: Union[Dict[str, Any], None, Unset]
        if isinstance(self.thresholds, Unset):
            thresholds = UNSET
        elif isinstance(self.thresholds, Thresholds):
            thresholds = self.thresholds.to_dict()
        else:
            thresholds = self.thresholds

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
            }
        )
        if indexes is not UNSET:
            field_dict["indexes"] = indexes
        if thresholds is not UNSET:
            field_dict["thresholds"] = thresholds

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.thresholds import Thresholds

        d = src_dict.copy()
        field = d.pop("field")

        def _parse_indexes(data: object) -> Union[List[int], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                indexes_type_0 = cast(List[int], data)

                return indexes_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[int], None, Unset], data)

        indexes = _parse_indexes(d.pop("indexes", UNSET))

        def _parse_thresholds(data: object) -> Union["Thresholds", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                thresholds_type_1 = Thresholds.from_dict(data)

                return thresholds_type_1
            except:  # noqa: E722
                pass
            return cast(Union["Thresholds", None, Unset], data)

        thresholds = _parse_thresholds(d.pop("thresholds", UNSET))

        data_path = cls(
            field=field,
            indexes=indexes,
            thresholds=thresholds,
        )

        data_path.additional_properties = d
        return data_path

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
