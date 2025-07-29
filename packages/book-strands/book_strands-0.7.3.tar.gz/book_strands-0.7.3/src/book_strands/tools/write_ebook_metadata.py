import logging
import os
import subprocess

from strands import tool

from book_strands.utils import ebook_meta_binary, is_valid_ebook

log = logging.getLogger(__name__)


@tool
def write_ebook_metadata(file_path: str, metadata: dict) -> dict:
    """
    Write metadata to ebook files using Calibre's ebook-meta CLI tool.

    Args:
        file_path (str): Path to the ebook file
        metadata (dict): A dictionary containing metadata to write. All fields are optional. Supported keys:
        {
            "title": str,
            "authors": list of str,
            "series": str,
            "series_index": str,
            "html_description": str,
        }

    Returns:
        A dictionary containing status of the operation in the format:
        {
            "status": "success" or "error",
            "message": "Description of the operation result"
        }
    """
    return _write_ebook_metadata(file_path, metadata)


def _write_ebook_metadata(file_path: str, metadata: dict) -> dict:
    """Write metadata to ebook files using Calibre's ebook-meta CLI tool."""

    log.info(f"Starting metadata write for file: {file_path!r}")
    log.debug(f"Metadata to write: {metadata}")

    file_path = os.path.expanduser(file_path)

    valid_ebook = is_valid_ebook(file_path)
    if valid_ebook["status"] != "success":
        return valid_ebook

    try:
        cmd = build_ebook_meta_command(file_path, metadata)

        log.debug(f"Running ebook-meta command: {' '.join(cmd)}")
        subprocess.check_output(cmd)
        log.info(f"Successfully wrote ebook metadata to {file_path!r}")

        return {
            "status": "success",
            "message": f"Metadata written successfully to {file_path!r}",
        }

    except subprocess.CalledProcessError as e:
        log.error(f"Error writing metadata: {e}")
        return {
            "status": "error",
            "message": f"Error writing ebook metadata: {e.stderr.decode('utf-8')} {e.stdout.decode('utf-8')}",
        }


def build_ebook_meta_command(file_path, metadata):
    """Build the ebook-meta command list for subprocess.run, using the correct path for macOS."""

    cmd = [ebook_meta_binary(), file_path]
    if "title" in metadata and metadata["title"]:
        cmd.append(f"--title={metadata['title']}")
    if "authors" in metadata and metadata["authors"]:
        cmd.append(f"--authors={' & '.join(metadata['authors'])}")
    if "series" in metadata and metadata["series"]:
        cmd.append(f"--series={metadata['series']}")
    if "series_index" in metadata and metadata["series_index"]:
        cmd.append(f"--index={str(metadata['series_index'])}")
    if "html_description" in metadata and metadata["html_description"]:
        cmd.append(f"--comments={metadata['html_description']}")
    return cmd
