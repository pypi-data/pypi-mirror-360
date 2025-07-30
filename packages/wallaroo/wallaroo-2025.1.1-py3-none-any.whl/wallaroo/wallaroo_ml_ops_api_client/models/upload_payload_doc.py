import json
from io import BytesIO
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import (
    define as _attrs_define,
    field as _attrs_field,
)

from ..types import File

if TYPE_CHECKING:
    from ..models.upload_request import UploadRequest


T = TypeVar("T", bound="UploadPayloadDoc")


@_attrs_define
class UploadPayloadDoc:
    """
    Attributes:
        file (File):
        metadata (UploadRequest):
    """

    file: File
    metadata: "UploadRequest"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        file = self.file.to_tuple()

        metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
                "metadata": metadata,
            }
        )

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        file = self.file.to_tuple()

        metadata = (
            None,
            json.dumps(self.metadata.to_dict()).encode(),
            "application/json",
        )

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                key: (None, str(value).encode(), "text/plain")
                for key, value in self.additional_properties.items()
            }
        )
        field_dict.update(
            {
                "file": file,
                "metadata": metadata,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.upload_request import UploadRequest

        d = src_dict.copy()
        file = File(payload=BytesIO(d.pop("file")))

        metadata = UploadRequest.from_dict(d.pop("metadata"))

        upload_payload_doc = cls(
            file=file,
            metadata=metadata,
        )

        upload_payload_doc.additional_properties = d
        return upload_payload_doc

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
