from typing import Any

from aiomexc.methods import MexcMethod
from aiomexc.types import MexcType


class MexcClientError(Exception):
    """
    Base exception for all mexc client errors.
    """


class DetailedMexcClientError(MexcClientError):
    """
    Base exception for all mexc client errors with a detailed message.
    """

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message})"


class MexcAPIError(DetailedMexcClientError):
    """
    Base exception for all mexc API errors.
    """

    label: str = "Mexc server says"

    def __init__(
        self,
        method: MexcMethod[MexcType],
        message: str,
        error_code: int | None = None,
    ) -> None:
        super().__init__(message=message)
        self.error_code = error_code
        self.method = method

    def __str__(self) -> str:
        original_message = super().__str__()
        if self.error_code:
            return f"{self.label} - {original_message} (error_code: {self.error_code})"
        return f"{self.label} - {original_message}"


class MexcNetworkError(MexcAPIError):
    """
    Exception raised when a network error occurs.
    """

    label: str = "HTTP Client says"


class MexcBadRequest(MexcAPIError):
    """
    Exception raised when request is malformed.
    """


class MexcNotFound(MexcAPIError):
    """
    Exception raised when order not found.
    """


class MexcApiKeyInvalid(MexcAPIError):
    """
    Exception raised when API key is invalid.
    """


class MexcApiKeyMissing(MexcAPIError):
    """
    Exception raised when API key is missing.
    """


class MexcApiIpNotAllowed(MexcAPIError):
    """
    Exception raised when API key is not allowed to access the IP.
    """


class MexcApiInvalidListenKey(MexcAPIError):
    """
    Exception raised when listen key is invalid.
    """


class MexcApiSignatureInvalid(MexcAPIError):
    """
    Exception raised when signature is invalid.
    """


class MexcApiOpenOrdersTooMany(MexcAPIError):
    """
    Exception raised when open orders are too many.
    """


class MexcApiInsufficientRights(MexcAPIError):
    """
    Exception raised when user has insufficient rights.
    """


class MexcApiRateLimitExceeded(MexcAPIError):
    """
    Exception raised when rate limit is exceeded.
    """


class MexcApiRequireKyc(MexcAPIError):
    """
    Exception raised when user requires KYC.
    """


class MexcApiOversold(MexcAPIError):
    """
    Exception raised when order is oversold.
    """


class MexcApiInsufficientBalance(MexcAPIError):
    """
    Exception raised when user has insufficient balance.
    """


class MexcApiRiskControlError(MexcAPIError):
    """
    Exception raised when risk control is triggered.
    """


class ClientDecodeError(MexcClientError):
    """
    Exception raised when client can't decode response. (Malformed response, etc.)
    """

    def __init__(self, message: str, original: Exception, data: Any) -> None:
        self.message = message
        self.original = original
        self.data = data

    def __str__(self) -> str:
        original_type = type(self.original)
        return (
            f"{self.message}\n"
            f"Caused from error: "
            f"{original_type.__module__}.{original_type.__name__}: {self.original}\n"
            f"Content: {self.data}"
        )


class MexcApiCredentialsMissing(DetailedMexcClientError):
    """
    Exception raised when credentials are missing.
    """

    def __init__(self, method: MexcMethod[MexcType]):
        super().__init__(
            f"Credentials are missing for {method.__api_method__!r} method"
        )


class MexcWsStreamsLimit(DetailedMexcClientError):
    """
    Exception raised when too many streams are subscribed.
    """

    def __init__(self, stream_count: int, max_streams: int = 30):
        super().__init__(
            f"You try to subscribe to {stream_count} streams, but the maximum is {max_streams}."
        )


class MexcWsNoStreamsProvided(DetailedMexcClientError):
    """
    Exception raised when no streams are provided.
    """

    def __init__(self):
        super().__init__("At least one stream must be provided to start listening.")


class MexcWsNoCredentialsProvided(MexcClientError):
    """
    Exception raised when no credentials are provided.
    """


class MexcWsInvalidStream(DetailedMexcClientError):
    """
    Exception raised when an invalid stream is provided.
    """

    def __init__(self, stream: str):
        super().__init__(f"You try to subscribe to an invalid stream: {stream}")


class MexcWsPrivateStream(DetailedMexcClientError):
    """
    Exception raised when a private stream is provided to a public connection.
    """

    def __init__(self, stream: str):
        super().__init__(
            f"You try to subscribe to a private stream without authentication: {stream}"
        )


class MexcWsConnectionClosed(DetailedMexcClientError):
    """
    Exception raised when the connection is closed.
    """

    def __init__(self):
        super().__init__("Connection closed")


class MexcWsUnknownMessageTypeError(DetailedMexcClientError):
    """
    Exception raised when the message type is unknown.
    """


class MexcWsConnectionTimeoutError(DetailedMexcClientError):
    """
    Exception raised when the connection timeout occurs.
    """


class MexcWsConnectionHandshakeError(DetailedMexcClientError):
    """
    Exception raised when the connection handshake fails.
    """

    def __init__(self, status: int):
        self.status = status
        super().__init__(f"Connection handshake failed with status: {status}")


class MexcWsConnectionNotEstablished(DetailedMexcClientError):
    """
    Exception raised when the connection is not established.
    """

    def __init__(self):
        super().__init__("Connection not established")
