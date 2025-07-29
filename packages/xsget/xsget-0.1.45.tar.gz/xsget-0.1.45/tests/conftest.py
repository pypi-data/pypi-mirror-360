# pylint: disable=C0114,C0116

import pytest
from scripttest import TestFileEnvironment


# See https://stackoverflow.com/a/62055409
@pytest.fixture(autouse=True)
def _change_test_dir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True, name="script_runner")
def fixture_script_runner(tmpdir):
    """Fixture to provide a CLI runner for testing."""

    def script_runner(cmd, *args, **kwargs):
        cwd = tmpdir / "scripttest"
        env = TestFileEnvironment(cwd)

        kwargs.setdefault("cwd", cwd)
        kwargs.setdefault("expect_error", True)

        return env.run(cmd, *args, **kwargs)

    return script_runner
