"""Custom exceptions for coverage plotting functionality."""


class UnsupportedFormatError(ValueError):
    """Raised when an unsupported output format is specified."""

    def __init__(self, format_: str, supported_formats: list[str]) -> None:
        """Initialize the exception.

        Args:
            format_: The unsupported format that was specified
            supported_formats: List of supported formats
        """
        supported = ", ".join(f"'{fmt}'" for fmt in supported_formats)
        super().__init__(f"Unsupported output format: '{format_}'. Supported formats: {supported}")
        self.format = format_
        self.supported_formats = supported_formats
