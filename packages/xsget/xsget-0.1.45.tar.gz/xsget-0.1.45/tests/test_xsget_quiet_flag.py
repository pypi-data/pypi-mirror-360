# pylint: disable=C0114,C0116


def test_quiet_logging(script_runner):
    ret = script_runner("xsget", "-q", "example.com")
    assert "DEBUG" not in ret.stdout
