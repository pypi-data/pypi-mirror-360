# pylint: disable=C0114,C0116

from xsget import __version__


def test_version(script_runner):
    ret = script_runner("xstxt", "-V")
    assert f"xstxt {__version__}" in ret.stdout
