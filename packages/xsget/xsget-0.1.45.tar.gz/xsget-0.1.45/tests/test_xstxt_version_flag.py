# pylint: disable=C0114,C0116


def test_purge_output_folder(script_runner):
    ret = script_runner("xstxt", "-d", "-p")
    assert "purge=True" in ret.stdout


def test_purge_output_folder_if_not_exists(script_runner):
    ret = script_runner("xstxt", "-d", "-p")
    assert "Purge output folder: " not in ret.stdout
