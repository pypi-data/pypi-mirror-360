import logging
import os

import click

from book_strands.utils import load_book_strands_config

from .agent import agent
from .constants import DEFAULT_OUTPUT_FORMAT

CONTEXT_SETTINGS = {"help_option_names": ["--help", "-h"]}

log = logging.getLogger(__name__)

# Load the configuration to ensure it exists before making requeests
config = load_book_strands_config()


def configure_logging(verbosity: int):
    """Configure logging based on verbosity level."""
    level = logging.WARN
    if verbosity == 1:
        level = logging.INFO
    elif verbosity == 2:
        level = logging.INFO
        logging.getLogger("strands").setLevel(logging.DEBUG)
    elif verbosity >= 3:
        level = logging.DEBUG

    # Remove all handlers from the root logger
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Add a new handler with our desired format
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root.addHandler(handler)

    # Set the level on the root logger
    root.setLevel(level)

    # Ensure the book_strands package logger inherits the level
    book_strands_logger = logging.getLogger("book_strands")
    book_strands_logger.propagate = True
    book_strands_logger.setLevel(level)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity (e.g., -v for INFO, -vv for DEBUG).",
)
def cli(verbose):
    """Book Strands CLI tool."""
    configure_logging(verbose)


@cli.command(name="agent")
@click.argument("output-path", type=click.Path())
@click.argument("query", nargs=-1, type=str)
@click.option(
    "--output-format",
    default=DEFAULT_OUTPUT_FORMAT,
    show_default=True,
    help="Output format for the renamed files",
)
@click.option("--disable-deletes", is_flag=True, help="Disable file deletions")
@click.option("--disable-downloads", is_flag=True, help="Disable file downloads")
@click.option("--disable-renames", is_flag=True, help="Disable file renames")
def run(
    query,
    output_path,
    output_format,
    disable_deletes,
    disable_downloads,
    disable_renames,
):
    """Run the agent with INPUT_QUERY and save results to OUTPUT_PATH."""
    query_str = " ".join(query)
    output_path = os.path.expanduser(output_path)

    agent(
        query=query_str,
        output_path=output_path,
        output_format=output_format,
        enable_deletions=not disable_deletes,
        enable_downloads=not disable_downloads,
        enable_renaming=not disable_renames,
    )


@cli.command()
@click.argument("input-path", type=click.Path(exists=True))
@click.argument("output-path", type=click.Path())
@click.option(
    "--output-format",
    default=DEFAULT_OUTPUT_FORMAT,
    show_default=True,
    help="Output format for the renamed files",
)
def import_local_books(input_path, output_path, output_format):
    """Import local ebook files from INPUT_PATH, update their metadata and rename them according to OUTPUT_FORMAT."""

    input_path = os.path.expanduser(input_path)
    output_path = os.path.expanduser(output_path)

    agent(
        query=f"Import local books from '{input_path}', update their metadata and rename them without downloading new books.",
        output_format=output_format,
        output_path=output_path,
    )
