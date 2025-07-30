from typing import Union

from fishjam.events import (
    ServerMessagePeerAdded,
    ServerMessagePeerConnected,
    ServerMessagePeerCrashed,
    ServerMessagePeerDeleted,
    ServerMessagePeerDisconnected,
    ServerMessagePeerMetadataUpdated,
    ServerMessageRoomCrashed,
    ServerMessageRoomCreated,
    ServerMessageRoomDeleted,
    ServerMessageTrackAdded,
    ServerMessageTrackMetadataUpdated,
    ServerMessageTrackRemoved,
)

ALLOWED_NOTIFICATIONS = (
    ServerMessageRoomCreated,
    ServerMessageRoomDeleted,
    ServerMessageRoomCrashed,
    ServerMessagePeerAdded,
    ServerMessagePeerDeleted,
    ServerMessagePeerConnected,
    ServerMessagePeerDisconnected,
    ServerMessagePeerMetadataUpdated,
    ServerMessagePeerCrashed,
    ServerMessageTrackAdded,
    ServerMessageTrackRemoved,
    ServerMessageTrackMetadataUpdated,
)

AllowedNotification = Union[
    ServerMessageRoomCreated,
    ServerMessageRoomDeleted,
    ServerMessageRoomCrashed,
    ServerMessagePeerAdded,
    ServerMessagePeerDeleted,
    ServerMessagePeerConnected,
    ServerMessagePeerDisconnected,
    ServerMessagePeerMetadataUpdated,
    ServerMessagePeerCrashed,
    ServerMessageTrackAdded,
    ServerMessageTrackRemoved,
    ServerMessageTrackMetadataUpdated,
]
