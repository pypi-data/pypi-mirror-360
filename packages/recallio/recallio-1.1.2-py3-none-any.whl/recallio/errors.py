"""Custom exceptions for Recallio client."""

class RecallioAPIError(Exception):
    """Exception raised when the Recallio API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(f"{status_code}: {message}" if status_code else message)
