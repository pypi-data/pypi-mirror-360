import logging
import os

from strands import Agent
from strands.telemetry import StrandsTelemetry

from book_strands.constants import BEDROCK_NOVA_PRO_MODEL, BOOK_HANDLING_PROMPT
from book_strands.tools import read_ebook_metadata, write_ebook_metadata
from book_strands.tools.filesystem import file_delete, file_search
from book_strands.utils import calculate_bedrock_cost  # type: ignore

from .tools import (
    download_ebook,
    file_move,
    lookup_books,
    path_list,
)

log = logging.getLogger(__name__)


if "OTEL_EXPORTER_OTLP_ENDPOINT" in os.environ.keys():
    strands_telemetry = StrandsTelemetry()
    strands_telemetry.setup_otlp_exporter()


def agent(
    output_path: str,
    output_format: str,
    query: str,
    enable_downloads: bool = True,
    enable_deletions: bool = True,
    enable_renaming: bool = True,
):
    system_prompt = f"""
You are a book downloader, renamer, and metadata fixer agent.
Your task is to download ebooks, rename them according to the provided format ({output_format}), and fix their metadata.
The output ebooks should be saved in the specified output path ({output_path}).
The output format should follow regular language conventions (capital letters, spaces, punctuation, etc) except where they would not be supported on a filesystem.

Check the output directory for the following:
- Any existing naming conventions to follow (e.g. author names using initials versus full names, etc)
- If the requested books have already been downloaded then do not download them again, just process the other books that are not downloaded if multiple have been requested)
- Unless you are asked otherwise, do not write metadata to existing files, only to new files that you download.

From the input query, if there is no clear action, extract the list of book titles and authors to download. If the query does not contain anything that can be resolved to a book title and/or author, return an error message indicating that no books were found. Use the available tools to look up books based on the query, and return a list of books that match the query.

If there are multiple books to download, use the download_ebook tool to download them all in a single request.
Only request to download each book once, even if it appears multiple times in the query.
The file extensions of ebooks do not matter, use the extensions as provided by the tools. When downloading a book you may be returned a different format ebook, this is acceptable.

When you are finshed, print a summary of what changes you made, which books were downloaded, what ones already existed and their file paths.

{BOOK_HANDLING_PROMPT}
"""

    model = BEDROCK_NOVA_PRO_MODEL
    tools = [
        lookup_books,
        read_ebook_metadata,
        write_ebook_metadata,
        path_list,
        file_search,
    ]

    if enable_downloads:
        tools.append(download_ebook)
    else:
        system_prompt += "\n\nYou will not download any ebooks."
    if enable_deletions:
        tools.append(file_delete)
    else:
        system_prompt += "\n\nYou will not delete any ebooks."
    if enable_renaming:
        tools.append(file_move)
    else:
        system_prompt += "\n\nYou will not rename any ebooks."

    a = Agent(system_prompt=system_prompt, model=model, tools=tools)

    response = a(query)
    log.info(f"Accumulated token usage: {response.metrics.accumulated_usage}")

    total_cost = calculate_bedrock_cost(
        response.metrics.accumulated_usage,
        model,
    )
    log.info(f"Total cost: US${total_cost:.3f}")

    return response
