# pylint: disable=C0114,C0116,W0621

import argparse
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


@pytest.fixture(autouse=True, name="cli_runner")
def fixture_cli_runner(tmpdir):
    def cli_runner(*args, **kwargs):
        cwd = tmpdir / "scripttest"
        env = TestFileEnvironment(cwd)
        kwargs.update({"cwd": cwd, "expect_error": True})
        return env.run("txt2ebook", *args, **kwargs)

    return cli_runner


@pytest.fixture(autouse=True, name="tte")
def fixture_tte(tmpdir):
    def cli_runner(*args, **kwargs):
        cwd = tmpdir / "scripttest"
        env = TestFileEnvironment(cwd)
        kwargs.update({"cwd": cwd, "expect_error": True})
        return env.run("tte", *args, **kwargs)

    return cli_runner


@pytest.fixture(autouse=True, name="infile")
def fixture_infile(tmpdir):
    def infile(filename):
        src = Path(FIXTURE_PATH, filename)
        des = Path(tmpdir, src.name)
        copyfile(src, des)
        return des

    return infile


@pytest.fixture(autouse=True, name="outfile")
def fixture_outfile(tmpdir):
    def outfile(filename):
        return Path(tmpdir, filename)

    return outfile


@pytest.fixture(name="config")
def fixture_config():
    return argparse.Namespace(
        **{
            "title": False,
            "author": False,
            "cover": None,
            "paragraph_separator": "\n\n",
            "re_delete": False,
            "re_replace": False,
            "re_delete_line": False,
            "re_volume_chapter": (),
            "re_volume": (),
            "re_chapter": (),
            "re_title": (),
            "re_author": (),
            "no_wrapping": False,
            "raise_on_warning": False,
            "width": False,
            "language": "zh-cn",
        }
    )
