import sys
from pathlib import Path

import pytest
import requests

from book_strands.tools.download_ebook import (
    Book,
    DownloadLimitReached,
    FileFormat,
    NoLoginsConfigured,
    ZLibSession,
    _download_ebook,
    get_logins,
)


# Fixtures for HTML responses
@pytest.fixture
def zlib_search_html_epub(tmp_path):
    with open("tests/fixtures/zl-search-results.html", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def zlib_profile_html_limits(tmp_path):
    with open("tests/fixtures/zl-profile-page.html", "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def fake_config(monkeypatch):
    config = {"zlib-logins": {"test@example.com": "password123"}}
    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    monkeypatch.setattr(download_ebook_mod, "load_book_strands_config", lambda: config)
    return config


def test_book_get_book_urls_finds_epub(monkeypatch, zlib_search_html_epub):
    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    session = requests.Session()

    def fake_get(*args, **kwargs):
        class Resp:
            status_code = 200
            text = zlib_search_html_epub

            def raise_for_status(self):
                pass

        return Resp()

    monkeypatch.setattr(session, "get", fake_get)
    book = Book(search_query="Test Book", language="English")
    monkeypatch.setattr(download_ebook_mod, "SUPPORTED_FORMATS", ["epub"])
    monkeypatch.setattr(download_ebook_mod, "ZLIB_BASE_URL", "https://zlib.example")
    monkeypatch.setattr(download_ebook_mod, "HEADERS", {"User-Agent": "test-agent"})

    book.get_book_urls(session)

    assert book.page_url == "https://zlib.example/book/1055305/9a6dda/harry-potter.html"
    assert book.file_format == FileFormat.EPUB
    assert book.download_url == "https://zlib.example/dl/1055305/0754e0"


def test_book_get_book_urls_raises_when_not_found(monkeypatch):
    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    session = requests.Session()

    def fake_get(*args, **kwargs):
        class Resp:
            status_code = 200
            text = "<html></html>"

            def raise_for_status(self):
                pass

        return Resp()

    monkeypatch.setattr(session, "get", fake_get)
    book = Book(search_query="Nonexistent Book", language="English")
    monkeypatch.setattr(download_ebook_mod, "SUPPORTED_FORMATS", ["epub"])
    monkeypatch.setattr(download_ebook_mod, "ZLIB_BASE_URL", "https://zlib.example")
    monkeypatch.setattr(download_ebook_mod, "HEADERS", {"User-Agent": "test-agent"})

    with pytest.raises(Exception):
        book.get_book_urls(session)


def test_zlibsession_login_success(monkeypatch):
    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    session = requests.Session()

    def fake_get(*args, **kwargs):
        class Resp:
            def __init__(self):
                self.text = ""

        return Resp()

    def fake_post(*args, **kwargs):
        class Resp:
            text = "login ok"
            status_code = 200

        return Resp()

    monkeypatch.setattr(session, "get", fake_get)
    monkeypatch.setattr(session, "post", fake_post)
    monkeypatch.setattr(download_ebook_mod, "HEADERS", {"User-Agent": "test-agent"})
    monkeypatch.setattr(
        download_ebook_mod, "ZLIB_LOGIN_URL", "https://zlib.example/login"
    )
    monkeypatch.setattr(ZLibSession, "_get_download_limits", lambda self: None)
    zs = ZLibSession(email="a@b.com", password="pw", session=session)
    assert zs.login() is True


def test_zlibsession_login_failure(monkeypatch):
    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    session = requests.Session()

    def fake_get(*args, **kwargs):
        class Resp:
            def __init__(self):
                self.text = ""

        return Resp()

    def fake_post(*args, **kwargs):
        class Resp:
            text = '"validationError":true'
            status_code = 200

        return Resp()

    monkeypatch.setattr(session, "get", fake_get)
    monkeypatch.setattr(session, "post", fake_post)
    monkeypatch.setattr(download_ebook_mod, "HEADERS", {"User-Agent": "test-agent"})
    monkeypatch.setattr(
        download_ebook_mod, "ZLIB_LOGIN_URL", "https://zlib.example/login"
    )
    zs = ZLibSession(email="a@b.com", password="pw", session=session)
    assert zs.login() is False


def test_zlibsession_get_download_limits(monkeypatch, zlib_profile_html_limits):
    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    session = requests.Session()

    def fake_get(*args, **kwargs):
        class Resp:
            text = zlib_profile_html_limits

        return Resp()

    monkeypatch.setattr(session, "get", fake_get)
    zs = ZLibSession(email="a@b.com", password="pw", session=session)
    monkeypatch.setattr(
        download_ebook_mod, "ZLIB_PROFILE_URL", "https://zlib.example/profile"
    )
    zs._get_download_limits()
    assert zs.downloads_used >= 0
    assert zs.downloads_max > 0


def test_zlibsession_download_book_success(monkeypatch, tmp_path):
    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    session = requests.Session()

    def fake_get(*args, **kwargs):
        class Resp:
            status_code = 200

            def iter_content(self, chunk_size):
                return [b"abc", b"def"]

            def raise_for_status(self):
                pass

        return Resp()

    monkeypatch.setattr(session, "get", fake_get)
    zs = ZLibSession(email="a@b.com", password="pw", session=session)
    zs.downloads_used = 0
    zs.downloads_max = 2
    book = Book(
        search_query="Test",
        file_format=FileFormat.EPUB,
        download_url="http://example.com/file",
    )
    monkeypatch.setattr(
        download_ebook_mod,
        "ensure_file_has_extension",
        lambda p, ext: str(tmp_path / f"file.{ext}"),
    )
    out_path = tmp_path / "file.epub"
    result = zs.download_book(book, str(out_path))
    assert Path(result).exists()
    with open(result, "rb") as f:
        content = f.read()
    assert content == b"abcdef"


def test_zlibsession_download_book_limit(monkeypatch):
    session = requests.Session()
    zs = ZLibSession(email="a@b.com", password="pw", session=session)
    zs.downloads_used = 2
    zs.downloads_max = 2
    book = Book(
        search_query="Test",
        file_format=FileFormat.EPUB,
        download_url="http://example.com/file",
    )
    with pytest.raises(DownloadLimitReached):
        zs.download_book(book, "somefile.epub")


def test_get_logins_success(fake_config):
    logins = get_logins()
    assert logins == [("test@example.com", "password123")]


def test_get_logins_no_logins(monkeypatch):
    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    monkeypatch.setattr(download_ebook_mod, "load_book_strands_config", lambda: {})
    with pytest.raises(NoLoginsConfigured):
        get_logins()


def test__download_ebook_success(monkeypatch, fake_config, tmp_path):
    # Patch ZLibSession to always succeed
    class FakeSession:
        def __init__(self, **kwargs):
            self.email = kwargs.get("email")
            self.password = kwargs.get("password")
            self.downloads_used = 0
            self.downloads_max = 10
            self.logged_in = False

        def login(self):
            return True

        def download_book(self, book, path):
            p = tmp_path / "file.epub"
            p.write_bytes(b"abc")
            return str(p)

    download_ebook_mod = sys.modules["book_strands.tools.download_ebook"]
    monkeypatch.setattr(download_ebook_mod, "ZLibSession", FakeSession)
    monkeypatch.setattr(
        download_ebook_mod, "get_logins", lambda: [("test@example.com", "pw")]
    )
    books = [{"search_query": "Test", "output_file_path": str(tmp_path / "file.epub")}]
    result = _download_ebook(books)
    assert result[0]["status"] == "success"
    assert Path(result[0]["output_file_path"]).exists()
