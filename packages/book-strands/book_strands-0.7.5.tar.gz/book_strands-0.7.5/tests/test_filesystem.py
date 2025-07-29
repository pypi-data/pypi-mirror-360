import os
import shutil
import tempfile
from unittest import mock

from book_strands.constants import SUPPORTED_FORMATS
from book_strands.tools.filesystem import (
    _file_delete,
    _file_move,
    _file_search,
    _path_list,
)


def test_path_list_success():
    """Test successful directory listing (only supported ebook files)."""
    from book_strands.constants import SUPPORTED_FORMATS

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create ebook and non-ebook files
        ebook_files = [f"book1.{SUPPORTED_FORMATS[0]}", f"book2.{SUPPORTED_FORMATS[1]}"]
        non_ebook_files = ["notes.txt", "cover.jpg", "README.md"]
        all_files = ebook_files + non_ebook_files
        for file_path in all_files:
            full_path = os.path.join(tmp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write("test content")
        # Add an ebook in a subdirectory
        subdir_ebook = os.path.join("subdir", f"nested.{SUPPORTED_FORMATS[2]}")
        full_subdir_ebook = os.path.join(tmp_dir, subdir_ebook)
        os.makedirs(os.path.dirname(full_subdir_ebook), exist_ok=True)
        with open(full_subdir_ebook, "w") as f:
            f.write("test content")
        # Call the function
        result = _path_list(tmp_dir)
        # Check the result
        assert result["status"] == "success"
        found_files = result["files"]
        # Only ebook files should be present
        expected_ebooks = [os.path.join(tmp_dir, f) for f in ebook_files]
        expected_ebooks.append(os.path.join(tmp_dir, subdir_ebook))
        assert set(found_files) == set(expected_ebooks)


def test_path_list_directory_not_found():
    """Test directory not found error."""
    result = _path_list("/nonexistent/directory")

    assert result["status"] == "error"
    assert "Directory not found" in result["message"]


def test_path_list_exception():
    """Test exception handling."""
    with mock.patch("os.walk", side_effect=Exception("Test error")):
        result = _path_list(os.path.expanduser("~"))

        assert result["status"] == "error"
        assert "Test error" in result["message"]


def test_path_list_success_only_ebooks():
    """Test directory listing only returns supported ebook files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create ebook and non-ebook files
        ebook_files = [f"book1.{SUPPORTED_FORMATS[0]}", f"book2.{SUPPORTED_FORMATS[1]}"]
        non_ebook_files = ["notes.txt", "cover.jpg", "README.md"]
        all_files = ebook_files + non_ebook_files
        for file_path in all_files:
            full_path = os.path.join(tmp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write("test content")
        # Add an ebook in a subdirectory
        subdir_ebook = os.path.join("subdir", f"nested.{SUPPORTED_FORMATS[2]}")
        full_subdir_ebook = os.path.join(tmp_dir, subdir_ebook)
        os.makedirs(os.path.dirname(full_subdir_ebook), exist_ok=True)
        with open(full_subdir_ebook, "w") as f:
            f.write("test content")
        # Call the function
        result = _path_list(tmp_dir)
        # Check the result
        assert result["status"] == "success"
        found_files = result["files"]
        # Only ebook files should be present
        expected_ebooks = [os.path.join(tmp_dir, f) for f in ebook_files]
        expected_ebooks.append(os.path.join(tmp_dir, subdir_ebook))
        assert set(found_files) == set(expected_ebooks)


def test_file_move_success():
    """Test successful file move."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        source_path = tmp.name

    destination_path = os.path.join(tempfile.gettempdir(), "moved_file.txt")

    # Call the function
    result = _file_move(source_path, destination_path)

    # Check the result
    assert result["status"] == "success"
    assert f"Moved '{source_path}' to '{destination_path}'" in result["message"]
    assert os.path.exists(destination_path)

    # Clean up
    os.remove(destination_path)


def test_file_move_source_not_found():
    """Test file move with nonexistent source."""
    source_path = "/nonexistent/file.txt"
    destination_path = os.path.join(tempfile.gettempdir(), "moved_file.txt")

    # Call the function
    result = _file_move(source_path, destination_path)

    # Check the result
    assert result["status"] == "error"
    # The actual error message contains the specific OS error


def test_file_move_overwrite_destination():
    """Test file move with existing destination."""
    # Create source file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"source content")
        source_path = tmp.name

    # Create destination file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"destination content")
        destination_path = tmp.name

    # Call the function
    result = _file_move(source_path, destination_path)

    # Check the result
    assert result["status"] == "success"
    assert os.path.exists(destination_path)

    # Verify content was overwritten
    with open(destination_path, "rb") as f:
        content = f.read()
        assert content == b"source content"

    # Clean up
    os.remove(destination_path)


def test_file_delete_file_success():
    """Test successful file deletion."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        file_path = tmp.name

    # Call the function
    result = _file_delete(file_path, False)

    # Check the result
    assert result["status"] == "success"
    assert f"Deleted '{file_path}'" in result["message"]
    assert not os.path.exists(file_path)


def test_file_delete_directory_success():
    """Test successful directory deletion."""
    # Create a temporary directory with files
    tmp_dir = tempfile.mkdtemp()
    test_file = os.path.join(tmp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test content")

    # Call the function
    result = _file_delete(tmp_dir, True)

    # Check the result
    assert result["status"] == "success"
    assert f"Deleted directory '{tmp_dir}'" in result["message"]
    assert not os.path.exists(tmp_dir)


def test_file_delete_file_not_found():
    """Test file deletion with nonexistent file."""
    file_path = "/nonexistent/file.txt"

    # Call the function
    result = _file_delete(file_path, False)

    # Check the result
    assert result["status"] == "error"
    # The actual error message contains the specific OS error


def test_file_delete_directory_not_found():
    """Test directory deletion with nonexistent directory."""
    dir_path = "/nonexistent/directory"

    # Call the function
    result = _file_delete(dir_path, True)

    # Check the result
    assert result["status"] == "error"
    # The actual error message contains the specific OS error


def test_file_delete_directory_without_flag():
    """Test attempting to delete a directory without is_directory=True."""
    # Create a temporary directory
    tmp_dir = tempfile.mkdtemp()

    try:
        # Call the function with is_directory=False
        result = _file_delete(tmp_dir, False)

        # Check the result
        assert result["status"] == "error"
        # Directory should still exist
        assert os.path.exists(tmp_dir)
    finally:
        # Clean up
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)


def test_file_search_success():
    """Test searching for ebook files by title and author."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create ebook files with title and author in filename
        ebook1 = f"The Great Gatsby - F. Scott Fitzgerald.{SUPPORTED_FORMATS[0]}"
        ebook2 = f"gatsby fitzgerald.{SUPPORTED_FORMATS[1]}"
        unrelated = f"Another Book - Someone Else.{SUPPORTED_FORMATS[0]}"
        files = [ebook1, ebook2, unrelated]
        for fname in files:
            with open(os.path.join(tmp_dir, fname), "w") as f:
                f.write("test content")
        # Call the function
        result = _file_search("Gatsby", "Fitzgerald", tmp_dir)
        assert result["status"] == "success"
        found = result["files"]
        assert any("gatsby" in os.path.basename(f).lower() for f in found)
        assert all("fitzgerald" in os.path.basename(f).lower() for f in found)
        # Only the two matching ebooks should be found
        assert len(found) == 2


def test_file_search_no_match():
    """Test searching for ebook files with no matches."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        with open(
            os.path.join(tmp_dir, f"Unrelated Book.{SUPPORTED_FORMATS[0]}"), "w"
        ) as f:
            f.write("test content")
        result = _file_search("Nonexistent", "Nobody", tmp_dir)
        assert result["status"] == "success"
        assert result["files"] == []


def test_file_search_exception():
    """Test exception handling in _file_search."""
    with mock.patch("os.walk", side_effect=Exception("Test error")):
        result = _file_search("title", "author", os.path.expanduser("~"))
        assert result["status"] == "error"
        assert "Test error" in result["message"]
