import logging
import os
import sys
from configparser import ConfigParser
from functools import lru_cache

from strands.types.event_loop import Usage
from strands.types.models import Model

from book_strands.constants import CONFIG_FILE_PATH, SUPPORTED_FORMATS

log = logging.getLogger(__name__)


def file_extension(file_path):
    """Get the file extension of a file"""
    _, ext = os.path.splitext(file_path)
    return ext.lower()


@lru_cache(maxsize=1)
def load_book_strands_config() -> ConfigParser:
    """Loads and caches the config from ~/.book-strands.conf as a ConfigParser object."""
    config_path = os.path.expanduser(CONFIG_FILE_PATH)
    config = ConfigParser()
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")
    config.read(config_path)
    return config


def ebook_meta_binary():
    """Get the path to the ebook-meta binary"""
    if sys.platform == "darwin":
        return "/Applications/calibre.app/Contents/MacOS/ebook-meta"
    else:
        return "ebook-meta"


BEDROCK_MODEL_PRICING = {
    "us.amazon.nova-pro-v1:0": {
        "input": 0.0008,
        "output": 0.0032,
    },
    "us.anthropic.claude-3-7-sonnet-20250219-v1:0": {
        "input": 0.003,
        "output": 0.015,
    },
    # Add more models and their prices here as needed
}


def calculate_bedrock_cost(accumulated_usage: Usage, model: Model) -> float:
    """
    Calculate the total cost for Bedrock model usage based on model name.

    Args:
        accumulated_usage: Usage object with "inputTokens" and "outputTokens" attributes.
        model_name (str): The Bedrock model name/id.

    Returns:
        float: Total cost in USD.
    """
    model_name = model.get_config().get("model_id", "unknown_model")

    pricing = BEDROCK_MODEL_PRICING.get(model_name)
    if not pricing:
        log.error(f"No pricing found for model: {model_name}")
        return 0
    input_tokens = accumulated_usage["inputTokens"]
    output_tokens = accumulated_usage["outputTokens"]
    total_cost = (
        input_tokens / 1000 * pricing["input"]
        + output_tokens / 1000 * pricing["output"]
    )

    log.info(f"Total cost: US${total_cost:.3f}")
    return total_cost


def ensure_file_has_extension(file_path: str, extension: str) -> str:
    """Ensure a file has the correct extension, removing any existing extension if it has one"""
    if not file_path.endswith(extension):
        if extension.startswith("."):
            extension = extension[1:]
        file_path = os.path.splitext(file_path)[0]
        file_path = f"{file_path}.{extension}"
    return file_path


@lru_cache
def is_valid_ebook(file_path: str) -> dict:
    if not os.path.exists(file_path):
        log.error(f"Source file not found: {file_path}")
        return {
            "status": "error",
            "message": f"Source file not found: {file_path}",
        }

    ext = file_extension(file_path).strip(".").lower()
    if ext not in SUPPORTED_FORMATS:
        log.error(f"Unsupported file format: {ext}")
        return {
            "status": "error",
            "message": f"Unsupported file format: {ext}. Supported formats: {', '.join(SUPPORTED_FORMATS)}",
        }

    return {"status": "success"}
