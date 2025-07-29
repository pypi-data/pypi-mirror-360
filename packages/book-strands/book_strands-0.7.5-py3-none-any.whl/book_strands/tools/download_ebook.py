import logging
from enum import Enum
from os import makedirs
from os.path import dirname
from pathlib import Path
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, Field
from requests import Session
from requests.adapters import HTTPAdapter, Retry
from strands import tool

from book_strands.constants import (
    HEADERS,
    SUPPORTED_FORMATS,
    ZLIB_BASE_URL,
    ZLIB_LOGIN_URL,
    ZLIB_PROFILE_URL,
    ZLIB_SEARCH_URL,
)
from book_strands.utils import ensure_file_has_extension, load_book_strands_config

WAIT_TIME = 1  # seconds to wait between book downloads and retries

log = logging.getLogger(__name__)


class FileFormat(Enum):
    EPUB = "epub"
    PDF = "pdf"
    MOBI = "mobi"
    AZW3 = "azw3"
    FB2 = "fb2"
    DJVU = "djvu"
    TXT = "txt"
    RTF = "rtf"
    DOC = "doc"
    DOCX = "docx"
    UNDEFINED = "undefined"


class Book(BaseModel):
    """
    Represents a book with its metadata and methods to fetch download links.
    Attributes:
        search_query (str): The search query for the book (e.g., title and author).
        language (str): The language of the book, default is "English".
        page_url (str): The URL of the book's page on Z-Library.
        file_format (FileFormat): The format of the book file.
        download_url (str): The URL to download the book file.
        file_path (str): The local path where the book file will be saved.
    """

    search_query: str = ""
    language: str = "English"
    page_url: str = Field(default="", exclude=True)
    file_format: FileFormat = Field(default=FileFormat.UNDEFINED, exclude=True)
    download_url: str = Field(default="", exclude=True)

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        validate_assignment=True,
    )

    def __repr__(self):
        return f"Book(search_query={self.search_query!r})"

    def get_book_urls(self, session: Session):
        """Search for a book on Z-Library and return a link to the first result."""

        if self.page_url:
            log.info(f"URL already set for book {self.search_query!r}")

        params = {
            "content_type": "book",
            "q": self.search_query,
            "languages[0]": self.language.lower(),
        }
        search_url = ZLIB_SEARCH_URL + "?" + urlencode(params)

        log.info(f"Searching for book: {self.search_query!r}")

        try:
            response = session.get(
                search_url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=10
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for ext in SUPPORTED_FORMATS:
                log.debug(f"Searching for books with extension: {ext}")
                book_cards = soup.find_all("z-bookcard", {"extension": ext})
                log.debug(f"Found {len(book_cards)} books with extension {ext}")
                matching_books = [b for b in book_cards]

                if matching_books:
                    log.info(f"Found matching books with extension {ext}")
                    href = str(matching_books[0].get("href"))  # type: ignore
                    download_url = str(matching_books[0].get("download"))  # type: ignore
                    if href:
                        log.info(
                            f"First matching book page URL: {href!r} with download URL: {download_url!r}"
                        )
                        self.page_url = ZLIB_BASE_URL + href
                        self.file_format = FileFormat(ext)
                        self.download_url = ZLIB_BASE_URL + download_url
                        return
                log.error(f"No matching books found with extension {ext}.")

            raise Exception("Unable to find the book " + self.search_query)
        except Exception as e:
            log.error(f"Error searching for book {self.search_query!r}: {e}")
            raise e


class DownloadLimitReached(Exception):
    """Raised when the Z-Library download limit has been reached for an account."""

    pass


class ZLibSession(BaseModel):
    email: str
    password: str
    downloads_used: int = 0
    downloads_max: int = 10  # Default max downloads
    session: Session
    logged_in: bool = False

    def __init__(self, **data):
        if "session" not in data or data["session"] is None:
            session = requests.Session()
            retries = Retry(
                total=5,
                backoff_factor=WAIT_TIME,  # wait 1s, 2s, 4s, etc. between retries
                status_forcelist=[500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
            )
            adapter = HTTPAdapter(max_retries=retries)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            data["session"] = session
        super().__init__(**data)

    class Config:
        arbitrary_types_allowed = True

    def login(self) -> bool:
        """Logs into Z-Library and returns success status."""
        if self.logged_in:
            log.info(f"Already logged in as {self.email}")
            return True

        self.session.get(ZLIB_LOGIN_URL, headers=HEADERS)

        login_data = {
            "isModal": "true",
            "email": self.email,
            "password": self.password,
            "site_mode": "books",
            "action": "login",
            "redirectUrl": "",
            "gg_json_mode": "1",
        }

        response = self.session.post(
            ZLIB_LOGIN_URL, data=login_data, headers=HEADERS, timeout=10
        )
        if not response:
            log.warning(f"Login failed for {self.email}: No response from server.")
            return False  # Give up after retries

        log.info(f"Login Attempt for: {self.email}")
        log.debug(f"Response Status Code: {response.status_code}")
        log.debug(f"Cookies After Login: {self.session.cookies.get_dict()}")

        success = '"validationError":true' not in response.text
        if success:
            log.info(f"Login successful for {self.email}")
            self._get_download_limits()
            self.logged_in = True

        return success

    def _get_download_limits(self):
        """Fetches the download limits from the user's profile page."""
        html = self.session.get(ZLIB_PROFILE_URL).text
        soup = BeautifulSoup(html, "html.parser")
        titles = soup.find_all("div", class_="caret-scroll__title")

        for title in titles:
            text = title.text.strip()
            log.debug(f"Raw download limit text: '{text}'")
            if "/" in text:
                try:
                    self.downloads_used, self.downloads_max = map(int, text.split("/"))
                    log.info(
                        f"Parsed limits - Used: {self.downloads_used}, Max: {self.downloads_max}"
                    )
                    return
                except ValueError:
                    log.error(f"Failed to parse download limits from text: '{text}'")

        log.error("Could not find download limits. Using default values.")

    def download_book(self, book: Book, destination_file_path: str) -> str:
        """Downloads the book to the specified file path."""
        if self.downloads_used >= self.downloads_max:
            log.warning(
                f"Download limit reached for {self.email}. Used: {self.downloads_used}, Max: {self.downloads_max}"
            )
            raise DownloadLimitReached(
                f"Download limit reached for {self.email}. Used: {self.downloads_used}, Max: {self.downloads_max}"
            )

        if not book.download_url:
            book.get_book_urls(self.session)
        destination_file_path = ensure_file_has_extension(
            destination_file_path, book.file_format.value
        )

        makedirs(dirname(destination_file_path), exist_ok=True)
        Path(destination_file_path).unlink(missing_ok=True)

        log.debug(
            f"Downloading book: {book.search_query!r} using {self.email!r} from {book.download_url!r} to {destination_file_path}"
        )

        try:
            response = self.session.get(
                book.download_url, stream=True, headers=HEADERS, timeout=10
            )
            response.raise_for_status()

            with open(destination_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.downloads_used += 1
            log.info(f"Downloaded book to {destination_file_path}")
            return destination_file_path

        except requests.RequestException as e:
            log.error(
                f"Error downloading book {book.search_query!r}: {e}",
                exc_info=True,
            )
            raise e


class NoLoginsConfigured(Exception):
    """Raised when no zlib-logins are found in the config file."""

    pass


def get_logins():
    """Returns a list of (email, password) tuples from the 'zlib-logins' key in the config."""
    config = load_book_strands_config()

    if "zlib-logins" in config:
        logins = config["zlib-logins"]
    else:
        log.error("'zlib-logins' key not found in config file.")
        raise NoLoginsConfigured("No 'zlib-logins' section found in config file.")

    result = []
    for email, password in logins.items():
        password = password.strip('"')
        result.append((email, password))

    if not result:
        log.error("'zlib-logins' key not found in config file.")
        raise NoLoginsConfigured(
            "No logins found in the 'zlib-logins' section of the config file."
        )
    return result


@tool
def download_ebook(books: list[dict]) -> list[dict]:
    """
    Downloads a list of books from Z-Library to the specified destination folder.
    Args:
        books (list[dict]): A list of dictionaries containing the search queries and matching output file paths to download each book to. Supported keys:
        [{
            "search_query": str,
            "output_file_path": str,
        }]
        search_query: The query to use for finding a book, e.g. the title and author
        output_file_path: The full canonical path to save the file to.
    Returns:
        A list of dicts containing the responses for each book
    """

    response = _download_ebook(books)

    log.info(f"Finishing download_ebook call with response: {response}")
    return response


def _download_ebook(books: list[dict]) -> list[dict]:
    sessions = [
        ZLibSession(email=email, password=password) for email, password in get_logins()
    ]
    session_index = 0

    log.info(f"Starting download process for {len(books)} books.")

    response: list[dict] = []
    for book in books:
        try:
            while session_index < len(sessions):
                session = sessions[session_index]
                session_index += 1
                if not session.login():
                    log.error(
                        f"Failed to log in with {session.email}. Trying next account."
                    )
                    continue

                try:
                    book["output_file_path"] = session.download_book(
                        Book(search_query=book["search_query"]),
                        book["output_file_path"],
                    )
                    log.info(f"Succesfully downloaded {book['search_query']!r}")
                    book["status"] = "success"
                    response.append(book)
                except DownloadLimitReached:
                    log.info("Switching accounts due to download limit reached.")
                    session_index += 1
                    continue
        except requests.RequestException as e:
            log.error(f"Network error while downloading {book['search_query']!r}: {e}")
            book["status"] = "failed"
        finally:
            response.append(book)

    return response
