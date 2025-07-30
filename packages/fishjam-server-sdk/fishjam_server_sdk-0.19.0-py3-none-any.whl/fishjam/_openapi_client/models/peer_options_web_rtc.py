from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.peer_options_web_rtc_metadata import PeerOptionsWebRTCMetadata


T = TypeVar("T", bound="PeerOptionsWebRTC")


@_attrs_define
class PeerOptionsWebRTC:
    """Options specific to the WebRTC peer"""

    enable_simulcast: Union[Unset, bool] = True
    """Enables the peer to use simulcast"""
    metadata: Union[Unset, "PeerOptionsWebRTCMetadata"] = UNSET
    """Custom peer metadata"""
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)
    """@private"""

    def to_dict(self) -> Dict[str, Any]:
        """@private"""
        enable_simulcast = self.enable_simulcast
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable_simulcast is not UNSET:
            field_dict["enableSimulcast"] = enable_simulcast
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """@private"""
        from ..models.peer_options_web_rtc_metadata import PeerOptionsWebRTCMetadata

        d = src_dict.copy()
        enable_simulcast = d.pop("enableSimulcast", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, PeerOptionsWebRTCMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = PeerOptionsWebRTCMetadata.from_dict(_metadata)

        peer_options_web_rtc = cls(
            enable_simulcast=enable_simulcast,
            metadata=metadata,
        )

        peer_options_web_rtc.additional_properties = d
        return peer_options_web_rtc

    @property
    def additional_keys(self) -> List[str]:
        """@private"""
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
