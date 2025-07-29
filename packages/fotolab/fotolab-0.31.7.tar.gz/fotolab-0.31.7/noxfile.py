# Copyright (c) 2022,2023,2024,2025 Kian-Meng Ang

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# mypy: disable-error-code="attr-defined"

"""Nox configuration."""

import argparse
import datetime

import nox


@nox.session(python="3.9")
def deps(session: nox.Session) -> None:
    """Update pre-commit hooks and deps."""
    _uv_install(session)
    session.run("pre-commit", "autoupdate", *session.posargs)


@nox.session(python="3.13")
def lint(session: nox.Session) -> None:
    """Run pre-commit tasks.

    For running selected task within pre-commit:

        nox -s lint -- ruff
    """
    _uv_install(session)
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def test(session: nox.Session) -> None:
    """Run test."""
    _uv_install(session)
    session.run(
        "uv", "run", "pytest", "--numprocesses", "auto", *session.posargs
    )


@nox.session(python="3.13")
def cov(session: nox.Session) -> None:
    """Run test coverage."""
    _uv_install(session)
    session.run(
        "uv",
        "run",
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
def readme(session: nox.Session) -> None:
    """Update console help menu to readme."""
    _uv_install(session)
    with open("README.md", "r+", encoding="utf8") as f:
        help_message = session.run("uv", "run", "fotolab", "-h", silent=True)
        help_codeblock = f"\n\n```console\n{help_message}```\n\n"

        content = f.read()
        marker = content.split("<!--help !-->")[1]
        readme_md = content.replace(marker, help_codeblock)

        for subcommand in [
            "animate",
            "auto",
            "border",
            "contrast",
            "info",
            "resize",
            "rotate",
            "montage",
            "sharpen",
            "watermark",
            "env",
        ]:
            help_message = session.run(
                "uv", "run", "fotolab", subcommand, "-h", silent=True
            )
            help_codeblock = f"\n\n```console\n{help_message}```\n\n"

            marker = readme_md.split(f"<!--help-{subcommand} !-->")[1]
            readme_md = readme_md.replace(marker, help_codeblock)

        f.seek(0)
        f.write(readme_md)
        f.truncate()


@nox.session(python="3.13", reuse_venv=True)
def release(session: nox.Session) -> None:
    """Bump release.

    To set which part of version explicitly:

        nox -s release -- major
        nox -s release -- minor
        nox -s release -- micro (default)
        nos -s release -- -h
    """
    _uv_install(session)

    parser = argparse.ArgumentParser(description="Release a semver version.")
    parser.add_argument(
        "semver",
        type=str,
        nargs="?",
        help="The type of semver release to make.",
        default="patch",
        choices={"major", "minor", "patch"},
    )
    args = parser.parse_args(args=session.posargs)

    session.run("uv", "version", "--bump", args.semver)
    after_version = session.run(
        "uv", "version", "--short", silent=True
    ).strip()

    date = datetime.date.today().strftime("%Y-%m-%d")
    before_header = "## [Unreleased]\n\n"
    after_header = f"## [Unreleased]\n\n## v{after_version} ({date})\n\n"
    _search_and_replace("CHANGELOG.md", before_header, after_header)

    # resync to update the bumped version to uv.lock
    _uv_install(session)

    session.run(
        "git",
        "commit",
        "--no-verify",
        "-am",
        f"Bump {after_version} release",
        external=True,
    )

    if input("Publish package to pypi? (y/n): ").lower() in ["y", "yes"]:
        session.run("flit", "build")
        session.run("flit", "publish")


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
