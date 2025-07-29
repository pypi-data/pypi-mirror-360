import logging
import os
import re
import subprocess

from strands import tool

from book_strands.constants import SUPPORTED_FORMATS
from book_strands.utils import ebook_meta_binary, file_extension

log = logging.getLogger(__name__)


@tool
def read_ebook_metadata(file_path: str) -> dict:
    """
    Extract metadata from EPUB or MOBI ebook files.

    Args:
        file_path: Path to the EPUB or MOBI file

    Returns:
        A dictionary containing metadata such as title, authors, series, series_number, and ISBN
    """
    return _read_ebook_metadata(file_path)


def _read_ebook_metadata(file_path: str) -> dict:
    file_path = os.path.expanduser(file_path)

    # Check if file exists
    if not os.path.exists(file_path):
        log.error(f"File not found: {file_path!r}")
        return {"status": "error", "message": f"File not found: {file_path!r}"}

    # Check file extension
    ext = file_extension(file_path).strip(".").lower()
    log.debug(f"File extension: {ext}")

    if ext not in SUPPORTED_FORMATS:
        log.error(
            f"Unsupported file format: {ext}. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
        )
        return {
            "status": "error",
            "message": f"Unsupported file format: {ext}. Supported formats: {', '.join(SUPPORTED_FORMATS)}",
        }

    try:
        output = subprocess.check_output([ebook_meta_binary(), file_path]).decode(
            "utf-8"
        )
        log.debug(f"raw ebook-meta output: {output}")
        metadata = parse_ebook_meta_output(output)
        metadata["status"] = "success"
        log.info(f"Successfully extracted metadata for {file_path!r}: {metadata!r}")
        return metadata

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8") if e.stderr else ""
        stdout = e.stdout.decode("utf-8") if e.stdout else ""
        log.error(f"Failed to read metadata for {file_path!r}: {stderr} {stdout}")
        return {
            "status": "error",
            "message": f"Failed to read metadata: {stderr} {stdout}",
        }


def parse_ebook_meta_output(s: str) -> dict:
    result = {}
    key = None
    value_lines = []
    lines = s.strip().splitlines()
    key_pattern = re.compile(r"^(.*?)\s*\s{3}:\s(.*)$")
    i = 0
    while i < len(lines):
        line = lines[i]
        match = key_pattern.match(line)
        if match:
            if key is not None:
                # Save previous key-value
                result[key] = (
                    "\n".join(value_lines).strip()
                    if key == "comments"
                    else " ".join(value_lines).strip()
                )
            key, first_value = match.group(1).lower(), match.group(2)
            value_lines = [first_value] if first_value else []
            if key == "comments":
                # Collect all lines until next key
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if key_pattern.match(next_line):
                        break
                    value_lines.append(next_line)
                    i += 1
                continue  # skip increment, already moved i
        else:
            value_lines.append(line)
        i += 1
    if key is not None:
        result[key] = (
            "\n".join(value_lines).strip()
            if key == "comments"
            else " ".join(value_lines).strip()
        )
    return result
