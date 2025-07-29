import logging
from functools import lru_cache

from strands import Agent, tool
from strands.types.models import Model
from strands_tools import http_request  # type: ignore

from book_strands.constants import BEDROCK_CLAUDE_37_MODEL, ZLIB_SEARCH_URL
from book_strands.utils import calculate_bedrock_cost

WAIT_TIME = 1  # seconds to wait between book downloads and retries

log = logging.getLogger(__name__)


@tool
@lru_cache(maxsize=32)
def lookup_books(
    query: str,
):
    """
    Lookup books based on the provided query and return a list of book titles and authors.

    Args:
        query (str): The query string containing the user's query, e.g. a book title and author, or a book series.

    Returns:
        response (list): A list of book titles and authors extracted from the query.
    """
    system_prompt = f"""You are a book information parser. Given a query about books, return a JSON list of dictionaries with book details. Only show results that are relevant to the query, for example if the query is about a specific book or series, return only those books, not omnibus or multi-book combinations. If the query is not about books, return an empty list. Do not do further lookups, or validate any dates. When lookuing up books, use "$title by $author" format.

IMPORTANT ACCURACY RULES:
- Only return books from your training data that you are ABSOLUTELY CERTAIN exist
- If you do not have enough information, look up the book using one of the below URLs, in order, only trying another if the first one fails:
  - {ZLIB_SEARCH_URL}
  - https://www.googleapis.com/books/v1/volumes?q=
  - https://www.goodreads.com/search?q=
- If the required information is provided in the search results, use that informaiton without further validation or lookups
- If you are unsure about any book details, omit that book entirely
- Do not create fictional books or combine real authors with made-up titles
- When uncertain about series information, set series fields to None rather than guessing
- If you cannot find any matching books with confidence, return an empty array []

For each book, include:
- "title": The book title
- "author": Primary author only
- "series": Series name (if part of a series, otherwise None)
- "series_index": Series position as decimal (e.g. 1.0, 2.5) if part of series, otherwise None

CRITICAL: Return only valid JSON array format. No additional text or explanations."""
    model: Model

    query = f"The user's query is: {query}"

    model = BEDROCK_CLAUDE_37_MODEL
    a = Agent(
        system_prompt=system_prompt,
        model=model,
        tools=[http_request],
    )

    response = a(query)
    log.info(f"Accumulated token usage: {response.metrics.accumulated_usage}")

    calculate_bedrock_cost(
        response.metrics.accumulated_usage,
        model,
    )

    return response
