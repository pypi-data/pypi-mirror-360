from collections import defaultdict
from typing import Union, cast, Optional, TYPE_CHECKING
from asgiref.typing import (
    Scope,
    HTTPScope,
    ASGISendCallable,
    ASGIReceiveCallable,
    WebSocketAcceptEvent,
    WebSocketScope,
)
from fast_query_parsers import parse_url_encoded_dict
from asgify.errors import ClientDisconnected
from asgify.status import WS_1000_NORMAL_CLOSURE, WS_1006_ABNORMAL_CLOSURE

if TYPE_CHECKING:
    from .app import Asgify


class BaseContext:
    def __init__(
        self,
        app: "Asgify",
        scope: Scope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
    ) -> None:
        """
        Initialize the BaseContext with the given ASGI application, scope, receive, and send callables.

        Args:
            app (Asgify): The ASGI application instance.
            scope (Scope): The ASGI connection scope.
            receive (ASGIReceiveCallable): The callable to receive ASGI messages.
            send (ASGISendCallable): The callable to send ASGI messages.
        """
        self.app = app
        self._scope = scope
        self._receive = receive
        self._send = send
        self._headers = {}
        self._params: dict[str, Union[str, list[str]]] = {}
        self.local = {}

    @property
    def path(self):
        """
        Return the request path from the ASGI scope.

        Returns:
            str: The request path.
        """
        return cast(str, self._scope.get("path"))

    @property
    def method(self):
        """
        Return the HTTP method from the ASGI scope.

        Returns:
            str: The HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
        """
        return cast(str, self._scope.get("method"))

    @property
    def scheme(self):
        """
        Return the URL scheme from the ASGI scope.

        Returns:
            str: The URL scheme (e.g., 'http', 'https').
        """
        return self._scope.get("scheme")

    @property
    def state(self):
        """
        Return the application state from the ASGI scope.

        Returns:
            dict: The application state dictionary.
        """
        return self._scope.get("state", {})

    @property
    def headers(self):
        """
        Return the request headers as a dictionary with header names as keys and lists of values.

        Returns:
            dict[str, list[str]]: The request headers.
        """
        if self._headers:
            return self._headers

        hdrs = defaultdict(list)
        for name, value in self._scope.get("headers", []):
            hdrs[name.decode("latin-1").lower()].append(value.decode("latin-1"))
        self._headers = dict(hdrs)
        return self._headers

    @property
    def params(self):
        """
        Return the query parameters as a dictionary.

        Returns:
            dict[str, Union[str, list[str]]]: The query parameters.
        """
        if self._params:
            return self._params

        query_string = self._scope.get("query_string", b"")
        self._params = parse_url_encoded_dict(query_string)
        return self._params

    async def receive(self):
        """
        Wrapper for the receive callable with connection close handling.
        Raises ClientDisconnected if the client disconnects.

        Returns:
            dict: The received ASGI message.
        Raises:
            ClientDisconnected: If the client disconnects.
        """
        message = await self._receive()
        if message["type"] in ("http.disconnect", "websocket.disconnect"):
            params = {}
            if message["type"] == "websocket.disconnect":
                params["code"] = message["code"]
                params["reason"] = message["reason"]
            raise ClientDisconnected(**params)
        return message

    async def send(self, message):
        """
        Wrapper for the send callable with connection close handling.
        Raises ClientDisconnected if the connection is closed unexpectedly.

        Args:
            message (dict): The ASGI message to send.
        Raises:
            ClientDisconnected: If the connection is closed unexpectedly.
        """
        try:
            await self._send(message)
        except OSError as e:
            raise ClientDisconnected() from e


class HTTPContext(BaseContext):
    def __init__(
        self,
        app: "Asgify",
        scope: HTTPScope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
    ) -> None:
        """
        Initialize the HTTPContext with the given ASGI application, HTTP scope, receive, and send callables.

        Args:
            app (Asgify): The ASGI application instance.
            scope (HTTPScope): The ASGI HTTP connection scope.
            receive (ASGIReceiveCallable): The callable to receive ASGI messages.
            send (ASGISendCallable): The callable to send ASGI messages.
        """
        super().__init__(app, scope, receive, send)

    async def read_body(self):
        """
        Asynchronously read the HTTP request body in chunks.
        Yields each chunk as bytes until the body is fully read.

        Yields:
            bytes: A chunk of the request body.
        """
        yield b""
        while True:
            message = await self.receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                yield body
                if not message.get("more_body", False):
                    break

    async def start(
        self,
        status: int,
        headers: Optional[dict[str, str]] = {},
        trailers: Optional[bool] = False,
    ):
        """
        Start the HTTP response by sending the response start message with status, headers, and optional trailers.

        Args:
            status (int): The HTTP status code.
            headers (Optional[dict[str, str]]): The response headers.
            trailers (Optional[bool]): Whether to expect HTTP trailers.
        """
        # Convert headers to iterable[tuple[bytes, bytes]]
        header_list = []
        for name, value in (headers or {}).items():
            header_list.append((name.encode("latin-1"), value.encode("latin-1")))

        await self.send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": header_list,
                "trailers": trailers,
            }
        )

    async def write(self, body: bytes):
        """
        Send a chunk of the HTTP response body.

        Args:
            body (bytes): The response body chunk to send.
        """
        await self.send({"type": "http.response.body", "body": body, "more_body": True})

    async def end(self, body: bytes = b""):
        """
        End the HTTP response by sending the final body chunk with more_body set to False.

        Args:
            body (bytes): The final response body chunk to send. Defaults to empty bytes.
        """
        await self.send(
            {"type": "http.response.body", "body": body, "more_body": False}
        )


class WebSocketContext(BaseContext):
    def __init__(
        self,
        app: "Asgify",
        scope: WebSocketScope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
    ) -> None:
        """
        Initialize a WebSocketContext instance.

        Parameters:
            app (Asgify): The ASGI application instance.
            scope (WebSocketScope): The ASGI WebSocket connection scope.
            receive (ASGIReceiveCallable): Callable to receive ASGI messages.
            send (ASGISendCallable): Callable to send ASGI messages.
        """
        super().__init__(app, scope, receive, send)
        self._connected = False

    async def accept(
        self, subprotocol: Optional[str] = None, headers: dict[str, str] = {}
    ):
        """
        Accept the WebSocket connection, optionally specifying a subprotocol and headers.

        Args:
            subprotocol (Optional[str]): The WebSocket subprotocol to use.
            headers (dict[str, str]): Additional headers to include in the accept message.
        Raises:
            AssertionError: If the WebSocket is already connected.
            ValueError: If the received message is not a WebSocket connect event.
        """
        assert not self.is_connected, "WebSocket is already connected"
        message = await self.receive()
        if message["type"] != "websocket.connect":
            raise ValueError(f"Expected websocket.connect, got {message['type']}")

        message = cast(WebSocketAcceptEvent, {"type": "websocket.accept"})
        if subprotocol:
            message["subprotocol"] = subprotocol

        # Convert headers to list[tuple[bytes, bytes]]
        header_list: list[tuple[bytes, bytes]] = []
        for name, value in headers.items():
            header_list.append((name.encode("latin-1"), value.encode("latin-1")))

        message["headers"] = header_list
        await self.send(message)
        self._connected = True

    @property
    def is_connected(self):
        """
        Return whether the WebSocket connection is established.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._connected

    async def receive_text(self) -> Optional[str]:
        """
        Receive a text message from the WebSocket client.

        Returns:
            Optional[str]: The received text message, or None if not present.
        Raises:
            AssertionError: If the WebSocket is not connected.
            ValueError: If the received message is not a WebSocket receive event or contains no text data.
        """
        assert self.is_connected, "WebSocket is not connected"

        message = await self.receive()
        if message["type"] != "websocket.receive":
            raise ValueError(f"Expected websocket.receive, got {message['type']}")

        if "text" not in message:
            raise ValueError("No text data in WebSocket message")

        return message["text"]

    async def receive_bytes(self) -> Optional[bytes]:
        """
        Receive a binary message from the WebSocket client.

        Returns:
            Optional[bytes]: The received binary data, or None if not present.
        Raises:
            AssertionError: If the WebSocket is not connected.
            ValueError: If the received message is not a WebSocket receive event or contains no binary data.
        """
        assert self.is_connected, "WebSocket is not connected"

        message = await self.receive()
        if message["type"] != "websocket.receive":
            raise ValueError(f"Expected websocket.receive, got {message['type']}")

        if "bytes" not in message:
            raise ValueError("No binary data in WebSocket message")

        return message["bytes"]

    async def send_text(self, text: str):
        """
        Send a text message to the WebSocket client.

        Args:
            text (str): The text message to send.
        Raises:
            AssertionError: If the WebSocket is not connected.
        """
        assert self.is_connected, "WebSocket is not connected"

        await self.send({"type": "websocket.send", "text": text, "bytes": None})

    async def send_bytes(self, data: bytes):
        """
        Send a binary message to the WebSocket client.

        Args:
            data (bytes): The binary data to send.
        Raises:
            AssertionError: If the WebSocket is not connected.
        """
        assert self.is_connected, "WebSocket is not connected"

        await self.send({"type": "websocket.send", "bytes": data, "text": None})

    async def close(
        self, code: int = WS_1000_NORMAL_CLOSURE, reason: Optional[str] = None
    ):
        """
        Close the WebSocket connection with the given code and optional reason.
        If not connected, accept the connection first.

        Args:
            code (int): The WebSocket close code.
            reason (Optional[str]): The reason for closing the connection.
        """
        if not self.is_connected:
            code = WS_1006_ABNORMAL_CLOSURE

        await self.send({"type": "websocket.close", "code": code, "reason": reason})
        self._connected = False
