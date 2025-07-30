from typing import Optional


class ClientDisconnected(Exception):
    """
    Exception raised when a client disconnects unexpectedly during HTTP or WebSocket communication.

    This exception is raised by the ASGI context wrappers when they detect that a client
    has disconnected from the server. This can happen during HTTP request processing or
    WebSocket communication when the client closes the connection prematurely.

    The exception can be raised in two scenarios:
    1. When receiving a disconnect message from the ASGI server
    2. When an OSError occurs during message sending (indicating connection loss)

    Attributes:
        code (Optional[int]): The WebSocket close code if this is a WebSocket disconnect.
                            For HTTP disconnects, this will be None.
        reason (Optional[str]): The reason for the disconnect, if provided by the client.
                            For HTTP disconnects, this will be None.

    Examples:
        >>> try:
        ...     message = await ctx.receive()
        ... except ClientDisconnected as e:
        ...     if e.code:
        ...         print(f"WebSocket closed with code {e.code}: {e.reason}")
        ...     else:
        ...         print("HTTP client disconnected")

    Note:
        This exception is automatically raised by the context wrappers in context.py
        and should typically be caught at the application level to handle client
        disconnections gracefully.
    """

    def __init__(
        self, code: Optional[int] = None, reason: Optional[str] = None
    ) -> None:
        """
        Initialize the ClientDisconnected exception.

        Args:
            code (Optional[int]): The WebSocket close code. Should be None for HTTP disconnects.
            reason (Optional[str]): The reason for the disconnect. Should be None for HTTP disconnects.
        """
        super().__init__()
        self.code = code
        self.reason = reason
