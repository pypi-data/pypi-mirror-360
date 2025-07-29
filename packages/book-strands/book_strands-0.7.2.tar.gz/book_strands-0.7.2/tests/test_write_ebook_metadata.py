import os
import tempfile
from unittest import mock

from book_strands.tools.write_ebook_metadata import (  # type: ignore
    _write_ebook_metadata,
)


def test_write_ebook_metadata_success():
    """Test successful metadata writing."""
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as tmp:
        tmp.write(b"dummy epub content")
        tmp_path = tmp.name

    metadata = {
        "title": "Test Title",
        "authors": ["Author One", "Author Two"],
        "series": "Test Series",
        "series_index": "1",
        "html_description": "Test Description",
    }

    with (
        mock.patch(
            "book_strands.tools.write_ebook_metadata.subprocess.check_output"
        ) as mock_check_output,
        mock.patch(
            "book_strands.tools.write_ebook_metadata.ebook_meta_binary",
            return_value="ebook-meta",
        ),
        mock.patch(
            "book_strands.tools.write_ebook_metadata.is_valid_ebook",
            return_value={"status": "success"}
        ),
        mock.patch(
            "book_strands.tools.write_ebook_metadata.os.path.exists",
            return_value=True
        ),
    ):
        result = _write_ebook_metadata(tmp_path, metadata)

        # Check that subprocess.check_output was called once
        assert mock_check_output.call_count == 1
        # Check the command arguments
        called_args = mock_check_output.call_args[0][0]
        assert called_args[0] == "ebook-meta"
        assert called_args[1] == tmp_path
        assert "--title=Test Title" in called_args
        assert "--authors=Author One & Author Two" in called_args
        assert "--series=Test Series" in called_args
        assert "--index=1" in called_args
        assert "--comments=Test Description" in called_args

    os.unlink(tmp_path)

    assert result["status"] == "success"
    assert "Metadata written successfully" in result["message"]


def test_write_ebook_metadata_unsupported_format():
    """Test unsupported file format."""
    # Create a temporary file with an unsupported format
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
        tmp.write(b"dummy content")
        tmp_path = tmp.name

    metadata = {"title": "Test Title"}

    # Mock is_valid_ebook to return an error for unsupported format
    with mock.patch(
        "book_strands.tools.write_ebook_metadata.is_valid_ebook",
        return_value={"status": "error", "message": "Unsupported file format: .txt"}
    ), mock.patch(
        "book_strands.tools.write_ebook_metadata.os.path.exists",
        return_value=True
    ):
        # Call the function
        result = _write_ebook_metadata(tmp_path, metadata)  # type: ignore

    # Clean up
    os.unlink(tmp_path)

    assert result["status"] == "error"
    assert "Unsupported file format" in result["message"]


def test_write_ebook_metadata_missing_source_file():
    """Test missing source file."""
    metadata = {"title": "Test Title"}
    dest_path = os.path.join(tempfile.gettempdir(), "modified.epub")

    # Call the function with a non-existent file
    result = _write_ebook_metadata("/nonexistent/file.epub", metadata)  # type: ignore

    assert result["status"] == "error"
    assert "Source file not found" in result["message"]
