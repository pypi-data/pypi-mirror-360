# pylint: disable=C0114,C0116

import pytest

DEFAULT_URL = "http://localhost"


def test_generating_default_config_file(script_runner):
    ret = script_runner("xsget", DEFAULT_URL, "-g")
    assert "Create config file: xsget.toml" in ret.stdout
    assert (
        "Cannot connect to host localhost:80 "
        "ssl:default [Connect call failed ('127.0.0.1', 80)]" in ret.stdout
    )


@pytest.mark.skip(reason="TODO")
def test_raise_exception_for_creating_duplicate_config_file(script_runner):
    _ = script_runner("xsget", DEFAULT_URL, "-g")
    ret = script_runner("xsget", DEFAULT_URL, "-g")
    logs = [
        "error: Existing config file found: xsget.toml",
        "xsget.ConfigFileExistsError: Existing config file found: xsget.toml",
    ]
    for log in logs:
        assert log in ret.stdout


@pytest.mark.skip(reason="TODO")
def test_generating_default_config_file_with_existing_found(script_runner):
    _ = script_runner("xsget", DEFAULT_URL, "-g")
    ret = script_runner("xsget", DEFAULT_URL, "-g")
    assert "Existing config file found: xsget.toml" in ret.stdout
