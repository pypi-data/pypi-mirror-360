import importlib
import subprocess

rem_mod = importlib.import_module("book_strands.tools.read_ebook_metadata")
parse_ebook_meta_output = rem_mod.parse_ebook_meta_output

# Example output from ebook-meta
EXAMPLE_META_OUTPUT = """Title               : The Burning God
Title sort          : Burning God, The
Author(s)           : R. F. Kuang [Kuang, R. F.]
Publisher           : HarperCollins UK
Book Producer       : calibre (7.23.0) [https://calibre-ebook.com]
Series              : The Poppy War #3
Languages           : eng
Timestamp           : 2024-12-31T06:53:35.274070+00:00
Published           : 2020-11-17T00:00:00+00:00
Identifiers         : isbn:9780008339166, google:DALEDwAAQBAJ, kobo:the-burning-god-the-poppy-war-book-3
Comments            : <div>
<p style="font-weight: 600">The exciting end to The Poppy War trilogy, R.F. Kuang's acclaimed, award-winning epic fantasy that combines the history of 20th-century China with a gripping world of gods and monsters, to devastating, enthralling effect.</p>
<p>After saving her nation of Nikan from foreign invaders and battling the evil Empress Su Daji in a brutal civil war, Fang Runin was betrayed by allies and left for dead.</p>
<p>Despite her losses, Rin hasn’t given up on those for whom she has sacrificed so much – the people of the southern provinces and especially Tikany, the village that is her home. Returning to her roots, Rin meets difficult challenges – and unexpected opportunities. While her new allies in the Southern Coalition leadership are sly and untrustworthy, Rin quickly realizes that the real power in Nikan lies with the millions of common people who thirst for vengeance and revere her as a goddess of salvation.</p>
<p>Backed by the masses and her Southern Army, Rin will use every weapon to defeat the Dragon Republic, the colonizing Hesperians, and all who threaten the shamanic arts and their practitioners.</p>
<p>As her power and influence grows, will she be strong enough to resist the Phoenix’s voice, urging her to burn the world and everything in it?</p></div>
Formats             : EPUB"""


def test_parse_ebook_meta_output():
    result = parse_ebook_meta_output(EXAMPLE_META_OUTPUT)
    assert result["title"] == "The Burning God"
    assert result["author(s)"] == "R. F. Kuang [Kuang, R. F.]"
    assert result["series"] == "The Poppy War #3"
    assert result["languages"] == "eng"
    assert result["formats"] == "EPUB"
    assert result["comments"].startswith("<div>")


def test_read_ebook_metadata_success(monkeypatch):
    monkeypatch.setattr(rem_mod, "ebook_meta_binary", lambda: "ebook-meta")
    monkeypatch.setattr(
        subprocess, "check_output", lambda *a, **kw: EXAMPLE_META_OUTPUT.encode("utf-8")
    )
    monkeypatch.setattr(rem_mod.os.path, "exists", lambda x: True)
    result = rem_mod._read_ebook_metadata("/fake/path/book.epub")
    assert result["status"] == "success"
    assert result["title"] == "The Burning God"
    assert result["series"] == "The Poppy War #3"


def test_read_ebook_metadata_file_not_found(monkeypatch):
    monkeypatch.setattr(rem_mod.os.path, "exists", lambda x: False)
    result = rem_mod._read_ebook_metadata("/fake/path/book.epub")
    assert result["status"] == "error"
    assert "File not found" in result["message"]


def test_read_ebook_metadata_unsupported_format(monkeypatch):
    monkeypatch.setattr(rem_mod.os.path, "exists", lambda x: True)
    monkeypatch.setattr(rem_mod, "file_extension", lambda x: "pdf")
    result = rem_mod._read_ebook_metadata("/fake/path/book.pdf")
    assert result["status"] == "error"
    assert "Unsupported file format" in result["message"]


def test_read_ebook_metadata_subprocess_error(monkeypatch):
    def raise_error(*a, **kw):
        raise subprocess.CalledProcessError(
            1, "ebook-meta", output=b"", stderr=b"error output"
        )

    monkeypatch.setattr(rem_mod, "ebook_meta_binary", lambda: "ebook-meta")
    monkeypatch.setattr(subprocess, "check_output", raise_error)
    monkeypatch.setattr(rem_mod.os.path, "exists", lambda x: True)
    result = rem_mod._read_ebook_metadata("/fake/path/book.epub")
    assert result["status"] == "error"
    assert "Failed to read metadata" in result["message"]
