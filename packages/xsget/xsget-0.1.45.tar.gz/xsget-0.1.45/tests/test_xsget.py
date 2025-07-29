# pylint: disable=C0114,C0116

import argparse
from pathlib import Path

import aiohttp
import pytest
from aioresponses import aioresponses

from xsget.xsget import (
    extract_urls,
    fetch_url_by_aiohttp,
    http_headers,
    url_to_filename,
)

DEFAULT_URL = "http://localhost"


def test_url_to_filename():
    expected = [
        ("http://a.com", "index.html"),
        ("http://a.com/", "index.html"),
        ("http://a.com/123", "123.html"),
        ("http://a.com/123/456", "456.html"),
        ("http://a.com/123/456/789", "789.html"),
        ("http://a.com/123.html", "123.html"),
        ("http://a.com/123.html?abc=def", "123.html"),
    ]
    for url, filename in expected:
        assert url_to_filename(url) == filename

    expected = [
        ("http://a.com/123?id=aaa", "id", "aaa.html"),
        ("http://a.com/456.php?tid=abc", "tid", "abc.html"),
        ("http://a.com/789.php?test=xyz&id=aaa", "id", "aaa.html"),
    ]
    for url, url_param, filename in expected:
        assert url_to_filename(url, url_param) == filename


def test_extract_urls():
    html = """
        <html>
        <body>
        <div class="toc">
            <a href="http://a.com/123"/>a</a>
            <a href="http://a.com/123/789.html"/>b</a>
            <a href="//a.com/987"/>c</a>
            <a href="/123/456"/>d</a>
            <a href="/123/654.html"/>e</a>
        </div>
        </body>
        </html>
    """

    expected_urls = [
        "http://a.com/123",
        "http://a.com/123/789.html",
        "http://a.com/987",
        "http://a.com/123/456",
        "http://a.com/123/654.html",
    ]

    css_paths = [
        "html body div.toc a",
        "html body div a",
        "body div.toc a",
        "div.toc a",
        "div a",
        "a",
    ]
    for css_path in css_paths:
        config = argparse.Namespace(
            url="http://a.com/123", link_css_path=css_path
        )
        assert extract_urls(html, config) == expected_urls


def test_user_agent():
    user_agent = http_headers()["User-Agent"]
    assert "Mozilla/5.0" in user_agent


@pytest.mark.skip(reason="TODO")
async def test_fetch_url_by_aiohttp(tmpdir):
    session = aiohttp.ClientSession()
    with aioresponses() as mocked:
        config = argparse.Namespace(
            url_param_as_filename="",
            output_dir="output",
        )
        mocked.get(DEFAULT_URL, status=200, body="test")

        resp = await fetch_url_by_aiohttp(session, DEFAULT_URL, config)
        assert resp.status == 200
        mocked.assert_called_once_with(DEFAULT_URL)

        with open(
            Path(tmpdir, "output", "index.html"), encoding="utf8"
        ) as file:
            assert file.read() == "test"

        await session.close()
