# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [0-based versioning](https://0ver.org/).

## [Unreleased]

## v0.1.45 (2025-07-06)

- Add `ruff format` `pre-commit` hook and code format
- Bump deps and `pre-commit` for `ruff`

## v0.1.44 (2025-06-29)

- Add missing deps to `nox` `doc` job
- Bump deps and `pre-commit` hook for `ruff`

## v0.1.43 (2025-06-22)

- Add `flit` to dev deps
- Add missing `pytest` plugins deps
- Bump deps and pre-commit hooks
- Update translations

## v0.1.42 (2025-06-15)

- Add missing dev deps for testing
- Bump deps
- Bump `pre-commit` hook for `ruff`
- Fix ruff pre-commit hook configuration
- Remove all linting `pre-commit` hooks replaced by `ruff`
- Remove duplicate command in `deps` job in `nox`
- Resolve `uv` not using nox's `venv` warning

## v0.1.41 (2025-06-08)

- Code format
- Fix missing deps for dev in `nox` session
- Fix reusing variable leading to incorrect type
- Fix type error
- Migrate `pre-commit` hooks to `ruff`
- Skip running `pre-commit` in active `venv` session

## v0.1.40 (2025-06-01)

- Bump deps
- Bump `pre-commit` hook for `mypy`
- Configure `pytest` `asyncio` mode
- Migrate from `pipenv` to `uv` for dependency management
- Update `deps` `nox` job to use `uv`

## v0.1.39 (2025-05-25)

- Bump deps
- Enhance `xstxt` test coverage and improve terminal output handling
- Handle invalid regex patterns gracefully
- Ignore llms files
- Mark async test with `pytest.mark.asyncio`

## v0.1.38 (2025-05-18)

- Bump deps
- Fix incorrect type
- Fix test with invalid book type
- Fix translation error
- Fix xsget help flag test

## v0.1.37 (2025-05-11)

- Bump deps
- Bump the min Python version for `pylint` check
- Disable `pylint` R0914 rule
- Update test to check file in output subdir

## v0.1.36 (2025-05-04)

- Bump deps
- Group flit build and publish together in `nox` release job
- Ignore W0718 rule in `pylint`
- Resolve C0209 consider-using-f-string
- Resolve R1710 inconsistent-return-statements

## v0.1.35 (2025-04-27)

- Bump deps
- Document Book class with docstrings for attributes
- Format logging when fetching urls
- Remove unnecessary comment
- Remove unused List import from book.py

## v0.1.34 (2025-04-20)

- Add missing type hintings
- Bump deps
- Refactor EnvironmentAction to remove unused arguments in **call** method

## v0.1.33 (2025-04-13)

- Bump deps
- Prompt to publish package in release `nox` job
- Refactor browser fetching with single instance

## v0.1.32 (2025-04-06)

- Add flit as deps for dev environment
- Build package after bump release
- Bump deps and `pre-commit` hook
- Commit files after release

## v0.1.31 (2025-03-30)

- Bump deps and `pre-commit` hook
- Improve type hints and docstrings for clarity
- Resolve W1203: Use lazy % formatting in logging functions
- Use `.format()` for translation in `generate_single_txt`

## v0.1.30 (2025-03-23)

- Bump deps and pre-commit hooks
- Improve error message for invalid regex in search_and_replace function
- Return config dict instead of parsed args in `_create_config`
- Update dosctrings for all classes and functions

## v0.1.29 (2025-03-16)

- Add .aider\* to .gitignore
- Add more test cases for `url_to_filename` function
- Add type hint for http_headers return value.
- Bump deps
- Fix grammar
- Handle IOError when writing to file in `fetch_url` functions.
- Raise ValueError in search_and_replace when regex substitution fails
- Refactor compile regex outside loop in `search_and_replace` function
- Update comment for `_load_config` function
- Update comments for `load_or_create_config` function
- Update more examples for `url_to_filename` function
- Update type hints for chapters in `generate_txt` functions
- Use only the first match in URL replacement

## v0.1.28 (2025-03-02)

- Add comment for cli fixture
- Add timeout to async `session.get`
- Add typehints
- Bump deps and `pre-commit` hook
- Fix conflicting -e flag
- Refactor cli test fixture
- Refactor load_and_create_config helper function
- Refactor string representation of chapter
- Return empty string if no content for wrapping
- Update comment and add examples to `url_to_filename` function

## v0.1.27 (2025-02-16)

- Bump deps
- Refactor config file handler
- Remove deprecated py38 support
- Set coverage to parallel mode
- Use ast.Constant as ast.Str is deprecated for Python 3.8+

## v0.1.26 (2025-02-09)

- Bump deps and `pre-commit` hooks
- Refactor `setup_logging` helper function

## v0.1.25 (2025-02-02)

- Bump deps and `pre-commit` hooks
- Resolve incompatible type warnings

## v0.1.24 (2025-01-26)

- Bump deps and `pre-commit` hook
- Remove `pybabel` deps
- Resolve `pylint` issue
- Resolve incompatible types in assignment

## v0.1.23 (2025-01-19)

- Add `-e` short flag for environment info
- Add empty line to separate `pylint` rule
- Update help message in readme
- Update translations

## v0.1.22 (2025-01-13)

- Pass correct type when generate txt files
- Resolve incompatible output filename type
- Update comment for `extract_text` function

## v0.1.21 (2025-01-05)

- Add missing license headers for Book and Chapter class
- Bump copyright years
- Bump deps and `pre-commit` hooks
- Sort fields in Book class by usage

## v0.1.20 (2024-12-29)

- Fix incorrect returned type
- Refactor `env` action, `Chapter` dataclass, and `_run_minitor` function
- Sync deps
- Update translations

## v0.1.19 (2024-12-22)

- Bump deps and `pre-commit` hooks
- Refactor extracting urls and title
- Use Pythonic approach to handling input files

## v0.1.18 (2024-12-15)

- Bump deps
- Refactor `setup_logging` and logging based on `-d` or `--debug` flag
- Refactor `url_to_filename`

## v0.1.17 (2024-12-08)

- Bump deps
- Fix missing output_dir in test
- Use Python major version for pyenv

## v0.1.16 (2024-12-01)

- Bump deps
- Update project correctly to support Python 3.9

## v0.1.15 (2024-11-24)

- Add missing `asynnc-mode` to `pytest`
- Drop support for Python 3.8
- Update pypi classifier

## v0.1.14 (2024-11-17)

- Add `-od` or `--output-dir` option to set default output path
- Add `release` session in `nox` to bump release
- Bump Python versions for `pyenv`
- Bump deps and `pre-commit` hooks
- Fix incorrect program name
- Migrate from `tox` to `nox`
- Remove subheaders in changelog
- Update readme from `readme` session in `nox`
- Update translations

## v0.1.13 (2024-03-31)

- Add `--env` flag to print debugging environment info
- Add example to `xstxt` command
- Add instruction on upgrade
- Bump deps and `pre-commit` hooks
- Fix extra quote on help message
- Fix newline in the `sys.version` output
- Flush progress output
- Update translations

## v0.1.12 (2024-01-21)

- Add `-p` or `--purge` flag to remove files from `--output-dir` option
- Add `-q` or `--quiet` flag to suppress logging
- Add `-y` or `--yes` flag to confirm any prompts
- Add missing classifier
- Allow scripttest runner to accept keyword arguments
- Bump project and pre-commit hooks deps
- Bump python versions for pyenv
- Replace `.prettierignore` with `pre-commit` config file
- Replace `pytest-console-script` with `scripttest` for testing
- Sort changelog url before the issue url
- Sort deps in `Pipfile`
- Sort test coverage report by coverage percentage
- Split test by console args/flags/options
- Support Python 3.12.0
- Switch to `Babel` for translations
- Update translations

## v0.1.11 (2023-08-13)

- Add `-od` or `--output-dir` option to set default output directory
- Add additional default hook for `pre-commit`
- Fix translation files not found error for `xstxt`
- Output txt file with yaml-inspired metadata header
- Remove checking for existing output filename
- Remove validating output file due to `-od` option
- Update `coverage` config to work with `tox`

## v0.1.10 (2023-07-16)

- Add Changelog page to project URL
- Add `-o` or `--overwrite` output filename arg
- Check for existing output filename when writing output for `xstxt`
- Fix cannot start xstxt due to uninitialized variable
- Fix coverage report due to typo error
- Fix inconsistent output sphinx output folder
- Fix missing `monitor` field in `xstxt.toml` file
- Remove deprecated FAQ for `xstxt` from doc
- Remove support for Python 3.7
- Remove unused `line-profiler` dep
- Remove warnings on deprecated `script_runner` calls
- Run coverage test in parallel by default
- Switch to `pipenv` to manage deps
- Update `tox` to use `pipenv` and use `tox.ini` as config
- Update changelog for consistent header style

## v0.1.9 (2023-05-28)

- Add watching mode, `-m` or `--monitor` for `xstxt` to regenerate the content
  from html files
- Fix session not closed during test
- Resolve raising generic exception
- Run test randomly by default
- Update PyPi's classifiers
- Update project classifiers and dependencies
- Use `pip install -e` to install local development copy

## v0.1.8 (2023-04-16)

- Add multiprocessor support for `pytest`
- Deprecate and remove `is_relative_url` and `relative_to_absolute_url`
  function in favour of lxml's `make_links_absolute` function
- Reduce number of browser session to prevent locking
- Refactor async tests
- Remove explicit config for async in tests
- Rename `-w` to `-wf` option to prevent duplicate with `--width`
- Set `index.html` as default filename for index page if missing
- Update translations

## v0.1.7 (2023-02-26)

- Add `-oi` or `--output-individual-file` to create a txt file for its
  corresponding html file
- Fix incorrect wrapping which was set to default `70`
- Remove escaped paragraph separator argument during argument parsing
- Remove the duplicate `_unescape` function
- Revise default environment for tox to run
- Show longer chapter title in debugging log

## v0.1.6 (2023-01-29)

- Format help message indentation to improve readability
- Support `-la` or `--language` option for metadata when exporting text file
- Support long options for all command option flags
- Use `-V` or `--version` flag instead of `-v` for show program version
- Use same logging output convention for error and exception message

## v0.1.5 (2022-12-30)

- Add `-fw` option to convert selected halfwidth characters to its fullwidth
  equivalent
- Add `-ps` option to set paragraph separator, default to two newlines (`\n\n`)
- Add `flake8-simplify` plugin in linting with Flake8
- Add missing package in contribution doc
- Bump support for latest Python versions in `pyenv`
- Fix extra help menu string when generating doc through Sphinx
- Fix layout for `width` argument help message
- Refactor handling of piping for default URL argument for `xsget`
- Refactor to use global config instead of individual config item
- Resolve W0621 issue raised by Pylint
- Set Pylint check to the minimum support Python version (3.7)
- Set default indentation characters `-ic` to `""` (disabled)
- Set default width `-w` for wrapping to `0` (disabled)
- Show debug logging for arguments and parsed arguments
- Show progress when processing multiple HTML files when debugging (`-d`) was disabled
- Split logging of downloading and saving HTML into two separate lines
- Support and test against Python 3.11
- Update missing type hints
- Update regex rule in `xstxt.toml` file to replace repeated empty line
- Width `-w` and indentation characters `-ic` option should work independently

## v0.1.4 (2022-10-14)

- Add `-b` option to crawl site by actual browser
- Add `-bd` option to set the delay to wait for a page to load in browser
- Add `-bs` option to set the number of session/page to open by browser
- Resolve mypy and pylint warnings
- Switch to pre-commit as default linter tool from tox
- Sync asyncio debugging with `-d` option
- Use simpler asyncio syntax that support Python 3.7

## v0.1.3 (2022-08-09)

- Add `-ic` option to set indent characters for a paragraph only if `-w` option
  is more than zero
- Add `-w` option to wrap text at specify length
- Fix not showing exact regex debug log
- Show individual config item in debug log
- Upgrade the TOML config file if there are changes in the config template file for both xsget and xstxt app

## v0.1.2 (2022-07-29)

- Add more html replacement regex rules to xstxt.toml
- Enable debug by default in config
- Fix invalid base_url in config
- Switch to pre-commit to manage code linting
- Update FAQ for xstxt usage

## v0.1.1 (2022-07-09)

- Fix missing description in PyPi page
- Test version using dynamic value

## v0.1.0 (2022-07-08)

- Initial public release
