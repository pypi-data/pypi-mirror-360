# pylint: disable=C0114,C0116


def test_quiet_debug_logging(script_runner):
    ret = script_runner("xstxt", "-d", "-q")
    assert "DEBUG" not in ret.stdout
