"""Unit tests for exceptions module."""

import pytest

from covmapy.exceptions import UnsupportedFormatError


class TestUnsupportedFormatError:
    """Test UnsupportedFormatError exception."""

    def test_initialization_and_message(self) -> None:
        """Test initialization and message formatting."""
        format_ = "pdf"
        supported_formats = ["html", "json"]

        error = UnsupportedFormatError(format_, supported_formats)

        expected_message = "Unsupported output format: 'pdf'. Supported formats: 'html', 'json'"
        assert str(error) == expected_message
        assert error.format == format_
        assert error.supported_formats == supported_formats

    def test_empty_supported_formats(self) -> None:
        """Test with empty supported formats list."""
        error = UnsupportedFormatError("pdf", [])

        expected_message = "Unsupported output format: 'pdf'. Supported formats: "
        assert str(error) == expected_message

    def test_inheritance(self) -> None:
        """Test that UnsupportedFormatError inherits from ValueError."""
        error = UnsupportedFormatError("pdf", ["html"])

        assert isinstance(error, ValueError)

    def test_raise_and_catch(self) -> None:
        """Test raising and catching the exception."""
        format_ = "unsupported"
        supported_formats = ["html", "json"]

        with pytest.raises(UnsupportedFormatError) as exc_info:
            raise UnsupportedFormatError(format_, supported_formats)

        caught_error = exc_info.value
        assert caught_error.format == format_
        assert caught_error.supported_formats == supported_formats
