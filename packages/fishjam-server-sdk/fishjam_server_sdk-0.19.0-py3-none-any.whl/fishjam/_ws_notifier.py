"""
Notifier listening to WebSocket events
"""

import asyncio
from typing import Callable, Literal, cast

import betterproto
from websockets import client
from websockets.exceptions import ConnectionClosed

from fishjam.events._protos.fishjam import (
    ServerMessage,
    ServerMessageAuthenticated,
    ServerMessageAuthRequest,
    ServerMessageEventType,
    ServerMessageSubscribeRequest,
    ServerMessageSubscribeResponse,
)
from fishjam.events.allowed_notifications import (
    ALLOWED_NOTIFICATIONS,
    AllowedNotification,
)


class FishjamNotifier:
    """
    Allows for receiving WebSocket messages from Fishjam.
    """

    def __init__(self, fishjam_url: str, management_token: str):
        """
        Create FishjamNotifier instance, providing the fishjam url and management token.
        """

        self._fishjam_url = (
            f"{fishjam_url.replace('http', 'ws')}/socket/server/websocket"
        )
        self._management_token: str = management_token
        self._websocket: client.WebSocketClientProtocol | None = None
        self._ready: bool = False

        self._ready_event: asyncio.Event | None = None

        self._notification_handler: Callable | None = None

    def on_server_notification(self, handler: Callable[[AllowedNotification], None]):
        """
        Decorator used for defining handler for Fishjam Notifications
        """
        self._notification_handler = handler
        return handler

    async def connect(self):
        """
        A coroutine which connects FishjamNotifier to Fishjam and listens for
        all incoming messages from the Fishjam.

        It runs until the connection isn't closed.

        The incoming messages are handled by the functions defined using the
        `on_server_notification` decorator.

        The handler have to be defined before calling `connect`,
        otherwise the messages won't be received.
        """
        async with client.connect(self._fishjam_url) as websocket:
            try:
                self._websocket = websocket
                await self._authenticate()

                if self._notification_handler:
                    await self._subscribe_event(
                        event=ServerMessageEventType.EVENT_TYPE_SERVER_NOTIFICATION
                    )

                self._ready = True
                if self._ready_event:
                    self._ready_event.set()

                await self._receive_loop()
            finally:
                self._websocket = None

    async def wait_ready(self) -> Literal[True]:
        """
        Waits until the notifier is connected and authenticated to Fishjam.

        If already connected, returns `True` immediately.
        """
        if self._ready:
            return True

        if self._ready_event is None:
            self._ready_event = asyncio.Event()

        return await self._ready_event.wait()

    async def _authenticate(self):
        if not self._websocket:
            raise RuntimeError("Websocket is not connected")

        msg = ServerMessage(
            auth_request=ServerMessageAuthRequest(token=self._management_token)
        )
        await self._websocket.send(bytes(msg))

        try:
            message = cast(bytes, await self._websocket.recv())
        except ConnectionClosed as exception:
            if "invalid token" in str(exception):
                raise RuntimeError("Invalid management token") from exception
            raise

        message = ServerMessage().parse(message)

        _type, message = betterproto.which_one_of(message, "content")
        assert isinstance(message, ServerMessageAuthenticated)

    async def _receive_loop(self):
        if not self._websocket:
            raise RuntimeError("Websocket is not connected")
        if not self._notification_handler:
            raise RuntimeError("Notification handler is not defined")

        while True:
            message = cast(bytes, await self._websocket.recv())
            message = ServerMessage().parse(message)
            _which, message = betterproto.which_one_of(message, "content")

            if isinstance(message, ALLOWED_NOTIFICATIONS):
                self._notification_handler(message)

    async def _subscribe_event(self, event: ServerMessageEventType):
        if not self._websocket:
            raise RuntimeError("Websocket is not connected")

        request = ServerMessage(subscribe_request=ServerMessageSubscribeRequest(event))

        await self._websocket.send(bytes(request))
        message = cast(bytes, await self._websocket.recv())
        message = ServerMessage().parse(message)
        _which, message = betterproto.which_one_of(message, "content")
        assert isinstance(message, ServerMessageSubscribeResponse)
