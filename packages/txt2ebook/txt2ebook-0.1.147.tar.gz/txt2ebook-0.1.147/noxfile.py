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

"""Nox configuration."""

import os
import shutil
import datetime

import nox

nox.options.default_venv_backend = "uv"


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
    session.run(
        "pre-commit",
        "run",
        "--all-files",
        *session.posargs,
    )


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session) -> None:
    """Runs test."""
    _uv_install(session)
    session.run("pytest", "--numprocesses", "auto", *session.posargs)


@nox.session(python="3.13")
def cov(session: nox.Session) -> None:
    """Runs test coverage."""
    _uv_install(session)
    session.run(
        "pytest",
        "--numprocesses",
        "auto",
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
        "src/txt2ebook",
        "-o",
        "src/txt2ebook/locales/txt2ebook.pot",
        "--omit-header",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "update",
        "-o",
        "src/txt2ebook/locales/en/LC_MESSAGES/txt2ebook.po",
        "-i",
        "src/txt2ebook/locales/txt2ebook.pot",
        "-l",
        "en",
        "--omit-header",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "update",
        "-o",
        "src/txt2ebook/locales/zh-cn/LC_MESSAGES/txt2ebook.po",
        "-i",
        "src/txt2ebook/locales/txt2ebook.pot",
        "-l",
        "zh_Hans",
        "--omit-header",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "update",
        "-o",
        "src/txt2ebook/locales/zh-tw/LC_MESSAGES/txt2ebook.po",
        "-i",
        "src/txt2ebook/locales/txt2ebook.pot",
        "-l",
        "zh_Hant",
        "--omit-header",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "compile",
        "-o",
        "src/txt2ebook/locales/en/LC_MESSAGES/txt2ebook.mo",
        "-i",
        "src/txt2ebook/locales/en/LC_MESSAGES/txt2ebook.po",
        "-l",
        "en",
        "--statistics",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "compile",
        "-o",
        "src/txt2ebook/locales/zh-cn/LC_MESSAGES/txt2ebook.mo",
        "-i",
        "src/txt2ebook/locales/zh-cn/LC_MESSAGES/txt2ebook.po",
        "-l",
        "zh_Hans",
        "--statistics",
        *session.posargs,
    )

    session.run(
        "pybabel",
        "compile",
        "-o",
        "src/txt2ebook/locales/zh-tw/LC_MESSAGES/txt2ebook.mo",
        "-i",
        "src/txt2ebook/locales/zh-tw/LC_MESSAGES/txt2ebook.po",
        "-l",
        "zh_Hant",
        "--statistics",
        *session.posargs,
    )


@nox.session(python="3.13", reuse_venv=True)
def readme(session: nox.Session) -> None:
    """Update console help menu to readme."""
    _uv_install(session)
    with open("README.md", "r+", encoding="utf8") as f:
        help_message = session.run("tte", "-h", silent=True)
        help_codeblock = f"\n\n```console\n{help_message}```\n\n"

        content = f.read()
        marker = content.split("<!--help !-->")[1]
        readme_md = content.replace(marker, help_codeblock)

        f.seek(0)
        f.write(readme_md)
        f.truncate()


@nox.session(python="3.13", reuse_venv=True)
def release(session: nox.Session) -> None:
    """Bump release."""
    _uv_install(session)

    before_version = session.run(
        "uv", "version", "--short", silent=True
    ).strip()
    session.run("uv", "version", "--bump", "patch")
    after_version = session.run(
        "uv", "version", "--short", silent=True
    ).strip()

    _search_and_replace(
        "src/txt2ebook/__init__.py", before_version, after_version
    )

    date = datetime.date.today().strftime("%Y-%m-%d")
    before_header = "## [Unreleased]\n\n"
    after_header = f"## [Unreleased]\n\n## v{after_version} ({date})\n\n"
    _search_and_replace("CHANGELOG.md", before_header, after_header)

    # resync to update the bumped version to uv.lock
    _uv_install(session)

    session.run(
        "git",
        "commit",
        "-am",
        f"Bump {after_version} release",
        external=True,
    )

    prompt = "Build and publish package to pypi? (y/n): "
    if input(prompt).lower() in ["y", "yes"]:
        dist_dir = os.path.join(os.getcwd(), "dist")
        shutil.rmtree(dist_dir)
        session.run("uv", "build")
        session.run("uv", "publish")


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
