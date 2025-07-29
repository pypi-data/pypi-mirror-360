# pylint: disable=C0114,C0116

from xsget import __version__


def test_env_output(script_runner):
    ret = script_runner("xsget", "--env")
    assert f"xsget: {__version__}" in ret.stdout
    assert "python: " in ret.stdout
    assert "platform: " in ret.stdout
