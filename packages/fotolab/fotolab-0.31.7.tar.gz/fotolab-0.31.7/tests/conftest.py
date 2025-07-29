# pylint: disable=C0114,C0116

import os
from pathlib import Path
from shutil import copyfile

import pytest
from scripttest import TestFileEnvironment

FIXTURE_PATH = Path(os.getcwd(), "tests", "fixtures")


# See https://stackoverflow.com/a/62055409
@pytest.fixture(autouse=True)
def _change_test_dir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)


@pytest.fixture(autouse=True, name="csv_file")
def fixture_csv_file(tmpdir):
    def csv_file(filename):
        src = Path(FIXTURE_PATH, filename)
        des = Path(tmpdir, src.name)
        copyfile(src, des)
        return des

    return csv_file


@pytest.fixture(autouse=True, name="image_file")
def fixture_image_file(tmpdir):
    def image_file(filename):
        src = Path(FIXTURE_PATH, filename)
        des = Path(tmpdir, src.name)
        copyfile(src, des)
        return des

    return image_file


@pytest.fixture(autouse=True, name="cli_runner")
def fixture_cli_runner(tmpdir):
    def cli_runner(*args, **kwargs):
        cwd = tmpdir / "scripttest"
        env = TestFileEnvironment(cwd)
        kwargs.update({"cwd": cwd, "expect_error": True})
        return env.run("fotolab", *args, **kwargs)

    return cli_runner
