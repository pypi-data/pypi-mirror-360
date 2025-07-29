# pylint: disable=C0114,C0116


def test_default_value_for_option_in_help(script_runner):
    ret = script_runner("xstxt", "-h")

    expects = [
        "set css path of chapter title (default: 'title')",
        "set css path of chapter body (default: 'body')",
        "set title of the novel (default: '不详')",
        "set author of the novel (default: '不详')",
        "set glob pattern of html files to process (default: '['./*.html']')",
        "set glob pattern of html files to exclude (default: '[]')",
        "set number of html files to process (default: '3')",
        "set output txt file name (default: 'book.txt')",
        "generate config file from options (default: 'xstxt.toml')",
        "load config from file (default: 'xstxt.toml')",
        "load config from file (default: 'xstxt.toml')",
        "set css path of chapter title (default: 'title')",
        "set css path of chapter body (default: 'body')",
        "set title of the novel (default: '不详')",
        "set author of the novel (default: '不详')",
        "set glob pattern of html files to process (default: '['./*.html']')",
        "set glob pattern of html files to exclude (default: '[]')",
        "set number of html files to process (default: '3')",
        "set output txt file name (default: 'book.txt')",
        "generate config file from options (default: 'xstxt.toml')",
        "load config from file (default: 'xstxt.toml')",
    ]

    for expect in expects:
        assert expect in ret.stdout
