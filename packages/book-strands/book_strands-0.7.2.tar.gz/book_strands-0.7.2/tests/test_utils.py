import os
import tempfile
from unittest import mock

from strands.types.event_loop import Usage

from book_strands.constants import SUPPORTED_FORMATS
from book_strands.utils import (
    calculate_bedrock_cost,
    ensure_file_has_extension,
    file_extension,
    is_valid_ebook,
)


def test_file_extension():
    """Test file_extension function."""
    assert file_extension("/path/to/file.txt") == ".txt"
    assert file_extension("/path/to/file.TXT") == ".txt"
    assert file_extension("/path/to/file") == ""
    assert file_extension("/path.to/file") == ""
    assert file_extension("/path/to/file.tar.gz") == ".gz"


def test_calculate_bedrock_cost():
    """Test calculate_bedrock_cost function."""
    # Create a mock model and usage
    mock_model = mock.MagicMock()
    mock_model.get_config.return_value = {"model_id": "us.amazon.nova-pro-v1:0"}

    # Test with some token usage
    usage = Usage(inputTokens=1000, outputTokens=500, totalTokens=1500)
    cost = calculate_bedrock_cost(usage, mock_model)
    expected_cost = (1000 / 1000 * 0.0008) + (500 / 1000 * 0.0032)
    assert cost == expected_cost

    # Test with zero tokens
    usage = {"inputTokens": 0, "outputTokens": 0}
    cost = calculate_bedrock_cost(usage, mock_model)
    assert cost == 0

    # Test with unknown model
    mock_model.get_config.return_value = {"model_id": "unknown_model"}
    usage = {"inputTokens": 1000, "outputTokens": 500}
    cost = calculate_bedrock_cost(usage, mock_model)
    assert cost == 0


def test_ensure_file_has_extension():
    """Test ensure_file_has_extension function."""
    # Test adding extension
    assert ensure_file_has_extension("/path/to/file", "txt") == "/path/to/file.txt"

    # Test with extension that already has a dot
    assert ensure_file_has_extension("/path/to/file", ".txt") == "/path/to/file.txt"

    # Test replacing extension
    assert (
        ensure_file_has_extension("/path/to/file.pdf", "epub") == "/path/to/file.epub"
    )

    # Test with same extension
    assert ensure_file_has_extension("/path/to/file.txt", "txt") == "/path/to/file.txt"


def test_is_valid_ebook():
    """Test is_valid_ebook function."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tmp:
        tmp.write(b"dummy content")
        valid_path = tmp.name

    try:
        # Test with valid file
        result = is_valid_ebook(valid_path)
        assert result["status"] == "success"

        # Test with non-existent file
        result = is_valid_ebook("/nonexistent/file.epub")
        assert result["status"] == "error"
        assert "Source file not found" in result["message"]

        # Test with unsupported format
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp:
            tmp.write(b"dummy content")
            invalid_path = tmp.name

        try:
            result = is_valid_ebook(invalid_path)
            assert result["status"] == "error"
            assert "Unsupported file format" in result["message"]
            assert all(fmt in result["message"] for fmt in SUPPORTED_FORMATS)
        finally:
            os.unlink(invalid_path)
    finally:
        os.unlink(valid_path)
