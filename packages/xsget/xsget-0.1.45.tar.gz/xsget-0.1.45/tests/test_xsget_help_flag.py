# pylint: disable=C0114,C0116


def test_repo_urls_in_help_message(script_runner):
    ret = script_runner("xsget", "-h")
    assert "website: https://github.com/kianmeng/xsget" in ret.stdout
    assert "issues: https://github.com/kianmeng/xsget/issues" in ret.stdout
