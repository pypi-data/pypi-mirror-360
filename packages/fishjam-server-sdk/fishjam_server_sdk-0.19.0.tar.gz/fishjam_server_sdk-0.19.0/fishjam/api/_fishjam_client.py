"""
Fishjam client used to manage rooms
"""

from dataclasses import dataclass
from typing import Any, List, Literal, Tuple, cast

from fishjam._openapi_client.api.room import add_peer as room_add_peer
from fishjam._openapi_client.api.room import create_room as room_create_room
from fishjam._openapi_client.api.room import delete_peer as room_delete_peer
from fishjam._openapi_client.api.room import delete_room as room_delete_room
from fishjam._openapi_client.api.room import get_all_rooms as room_get_all_rooms
from fishjam._openapi_client.api.room import get_room as room_get_room
from fishjam._openapi_client.api.room import refresh_token as room_refresh_token
from fishjam._openapi_client.api.viewer import generate_token as viewer_generate_token
from fishjam._openapi_client.models import (
    AddPeerJsonBody,
    Peer,
    PeerDetailsResponse,
    PeerOptionsWebRTC,
    PeerRefreshTokenResponse,
    RoomConfig,
    RoomConfigRoomType,
    RoomCreateDetailsResponse,
    RoomDetailsResponse,
    RoomsListingResponse,
    ViewerToken,
)
from fishjam._openapi_client.models.peer_options_web_rtc_metadata import (
    PeerOptionsWebRTCMetadata,
)
from fishjam._openapi_client.models.room_config_video_codec import RoomConfigVideoCodec
from fishjam.api._client import Client


@dataclass
class Room:
    """Description of the room state"""

    config: RoomConfig
    """Room configuration"""
    id: str
    """Room ID"""
    peers: List[Peer]
    """List of all peers"""


@dataclass
class RoomOptions:
    """Description of a room options"""

    max_peers: int | None = None
    """Maximum amount of peers allowed into the room"""
    video_codec: Literal["h264", "vp8"] | None = None
    """Enforces video codec for each peer in the room"""
    webhook_url: str | None = None
    """URL where Fishjam notifications will be sent"""
    room_type: Literal[
        "conference", "audio_only", "livestream", "full_feature", "broadcaster"
    ] = "conference"
    """The use-case of the room. If not provided, this defaults to conference."""
    public: bool = False
    """True if livestream viewers can omit specifying a token."""


@dataclass
class PeerOptions:
    """Options specific to the Peer"""

    enable_simulcast: bool = True
    """Enables the peer to use simulcast"""
    metadata: dict[str, Any] | None = None
    """Peer metadata"""


class FishjamClient(Client):
    """Allows for managing rooms"""

    def __init__(self, fishjam_url: str, management_token: str):
        """
        Create FishjamClient instance, providing the fishjam url and managment token.
        """
        super().__init__(fishjam_url=fishjam_url, management_token=management_token)

    def create_peer(
        self, room_id: str, options: PeerOptions | None = None
    ) -> Tuple[Peer, str]:
        """
        Creates peer in the room

        Returns a tuple (`Peer`, `PeerToken`) - the token is needed by Peer
        to authenticate to Fishjam.

        The possible options to pass for peer are `PeerOptions`.
        """
        options = options or PeerOptions()

        peer_type = "webrtc"
        peer_metadata = self.__parse_peer_metadata(options.metadata)
        peer_options = PeerOptionsWebRTC(
            enable_simulcast=options.enable_simulcast, metadata=peer_metadata
        )
        json_body = AddPeerJsonBody(type=peer_type, options=peer_options)

        resp = cast(
            PeerDetailsResponse,
            self._request(room_add_peer, room_id=room_id, json_body=json_body),
        )

        return (resp.data.peer, resp.data.token)

    def create_room(self, options: RoomOptions | None = None) -> Room:
        """
        Creates a new room
        Returns the created `Room`
        """
        options = options or RoomOptions()

        codec = None
        if options.video_codec:
            codec = RoomConfigVideoCodec(options.video_codec)

        config = RoomConfig(
            max_peers=options.max_peers,
            video_codec=codec,
            webhook_url=options.webhook_url,
            room_type=RoomConfigRoomType(options.room_type),
            public=options.public,
        )

        room = cast(
            RoomCreateDetailsResponse, self._request(room_create_room, json_body=config)
        ).data.room

        return Room(config=room.config, id=room.id, peers=room.peers)

    def get_all_rooms(self) -> List[Room]:
        """Returns list of all rooms"""

        rooms = cast(RoomsListingResponse, self._request(room_get_all_rooms)).data

        return [
            Room(config=room.config, id=room.id, peers=room.peers) for room in rooms
        ]

    def get_room(self, room_id: str) -> Room:
        """Returns room with the given id"""

        room = cast(
            RoomDetailsResponse, self._request(room_get_room, room_id=room_id)
        ).data

        return Room(config=room.config, id=room.id, peers=room.peers)

    def delete_peer(self, room_id: str, peer_id: str) -> None:
        """Deletes peer"""

        return self._request(room_delete_peer, id=peer_id, room_id=room_id)

    def delete_room(self, room_id: str) -> None:
        """Deletes a room"""

        return self._request(room_delete_room, room_id=room_id)

    def refresh_peer_token(self, room_id: str, peer_id: str) -> str:
        """Refreshes peer token"""

        response = cast(
            PeerRefreshTokenResponse,
            self._request(room_refresh_token, id=peer_id, room_id=room_id),
        )

        return response.data.token

    def create_livestream_viewer_token(self, room_id: str) -> str:
        """Generates viewer token for livestream rooms"""

        response = cast(
            ViewerToken, self._request(viewer_generate_token, room_id=room_id)
        )

        return response.token

    def __parse_peer_metadata(self, metadata: dict | None) -> PeerOptionsWebRTCMetadata:
        peer_metadata = PeerOptionsWebRTCMetadata()

        if not metadata:
            return peer_metadata

        for key, value in metadata.items():
            peer_metadata.additional_properties[key] = value

        return peer_metadata
