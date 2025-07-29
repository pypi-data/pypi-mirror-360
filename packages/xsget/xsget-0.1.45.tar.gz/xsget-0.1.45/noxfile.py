# Copyright (c) 2022,2023,2024 Kian-Meng Ang

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Generals Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# mypy: disable-error-code="attr-defined"
# pylint: disable=R0914

"""Nox configuration."""

import ast
import datetime

import nox
from packaging.version import Version


@nox.session(python="3.9")
def deps(session: nox.Session) -> None:
    """Update pre-commit hooks and deps."""
    _uv_install(session)
    session.run("pre-commit", "autoupdate", *session.posargs)


@nox.session(python="3.13")
def lint(session: nox.Session) -> None:
    """Run pre-commit tasks.

    For running selected task within pre-commit:

        nox -s lint -- pylint
    """
    _uv_install(session)
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session) -> None:
    """Run test."""
    _uv_install(session)
    session.run(
        "pytest",
        "--numprocesses",
        "auto",
        "--asyncio-mode=auto",
        *session.posargs,
    )


@nox.session(python="3.13")
def cov(session: nox.Session) -> None:
    """Run test coverage."""
    _uv_install(session)
    session.run(
        "pytest",
        "--numprocesses",
        "auto",
        "--asyncio-mode=auto",
        "--cov",
        "--cov-report=term",
        "--cov-report=html",
        *session.posargs,
    )


@nox.session(python="3.13")
def doc(session: nox.Session) -> None:
    """Build doc with sphinx."""
    _uv_install(session)
    session.run(
        "sphinx-build", "docs/source/", "docs/build/html", *session.posargs
    )


@nox.session(python="3.13")
def pot(session: nox.Session) -> None:
    """Update translations."""
    _uv_install(session)
    session.run(
        "pybabel",
        "extract",
        "xsget",
        "-o",
        "xsget/locales/xstxt.pot",
        "--omit-header",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "update",
        "-o",
        "xsget/locales/en/LC_MESSAGES/xstxt.po",
        "-i",
        "xsget/locales/xstxt.pot",
        "-l",
        "en",
        "--omit-header",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "update",
        "-o",
        "xsget/locales/zh/LC_MESSAGES/xstxt.po",
        "-i",
        "xsget/locales/xstxt.pot",
        "-l",
        "zh",
        "--omit-header",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "compile",
        "-o",
        "xsget/locales/en/LC_MESSAGES/xstxt.mo",
        "-i",
        "xsget/locales/en/LC_MESSAGES/xstxt.po",
        "-l",
        "en",
        "-f",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "compile",
        "-o",
        "xsget/locales/zh/LC_MESSAGES/xstxt.mo",
        "-i",
        "xsget/locales/zh/LC_MESSAGES/xstxt.po",
        "-l",
        "zh",
        "-f",
        *session.posargs,
    )


@nox.session(python="3.13", reuse_venv=True)
def release(session: nox.Session) -> None:
    """Bump release.

    To set which part of version explicitly:

        nox -s release -- major
        nox -s release -- minor
        nox -s release -- micro (default)
    """
    _uv_install(session)

    with open("xsget/__init__.py", "r", encoding="utf8") as f:
        tree = ast.parse(f.read())
        current_version = None
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target, value = node.targets[0], node.value
                if target.id == "__version__" and isinstance(
                    value, ast.Constant
                ):
                    current_version = value.s
                    break

        if current_version is None:
            raise ValueError("Missing __version__ variable in __init__.py")

        before_version = Version(current_version)

        (major, minor, micro) = (
            before_version.major,
            before_version.minor,
            before_version.micro,
        )
        if "major" in session.posargs:
            major = major + 1
            minor = 0
            micro = 0

        if "minor" in session.posargs:
            minor = minor + 1
            micro = 0

        if "micro" in session.posargs or session.posargs == []:
            micro = micro + 1

        after_version = f"{major}.{minor}.{micro}"
        _search_and_replace(
            "xsget/__init__.py", str(before_version), after_version
        )

        date = datetime.date.today().strftime("%Y-%m-%d")
        before_header = "## [Unreleased]\n\n"
        after_header = f"## [Unreleased]\n\n## v{after_version} ({date})\n\n"
        _search_and_replace("CHANGELOG.md", before_header, after_header)

        session.run(
            "git",
            "commit",
            "--no-verify",
            "-am",
            f"Bump {after_version} release",
            external=True,
        )

        response = input("Publish package to pypi? (y/n): ").lower()
        if response in ["y", "yes"]:
            session.run("flit", "build")
            session.run("flit", "publish")


@nox.session(python="3.13")
def readme(session: nox.Session) -> None:
    """Update console help menu to readme."""
    _uv_install(session)

    with open("README.md", "r+", encoding="utf8") as f:
        content = f.read()
        for app in ["xsget", "xstxt"]:
            help_message = session.run(app, "-h", silent=True)
            help_codeblock = f"\n\n```console\n{help_message}```\n\n"

            marker = content.split(f"<!--help-{app} !-->")[1]
            content = content.replace(marker, help_codeblock)

        f.seek(0)
        f.write(content)
        f.truncate()


def _search_and_replace(file, search, replace) -> None:
    with open(file, "r+", encoding="utf8") as f:
        content = f.read()
        content = content.replace(search, replace)
        f.seek(0)
        f.write(content)
        f.truncate()


def _uv_install(session: nox.Session) -> None:
    """Install the project and its development dependencies using uv.

    This also resolves the following error:
        warning: `VIRTUAL_ENV=.nox/lint` does not match the project environment
        path `.venv` and will be ignored

    See https://nox.thea.codes/en/stable/cookbook.html#using-a-lockfile
    """
    session.run_install(
        "uv",
        "sync",
        "--upgrade",
        "--all-packages",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
