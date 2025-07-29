# pylint: disable=C0114,C0116

import pytest


def test_default_format_is_epub(cli_runner, infile, outfile):
    txt = infile("sample.txt")
    epub = outfile("output/sample.epub")
    output = cli_runner(txt)
    assert f"Generate EPUB file: {str(epub)}" in output.stdout

    output = cli_runner("--help")
    assert "ebook format (default: 'epub')" in output.stdout


@pytest.mark.parametrize("option", ["-f", "--format"])
def test_set_format_to_epub(cli_runner, infile, option):
    txt = infile("sample.txt")
    output = cli_runner(option, "epub", txt)
    assert "Generate EPUB file:" in output.stdout


@pytest.mark.parametrize("option", ["-f", "--format"])
def test_set_format_to_txt(cli_runner, infile, option):
    txt = infile("sample.txt")
    output = cli_runner(option, "txt", txt)
    assert "Generate TXT file:" in output.stdout


@pytest.mark.parametrize("option", ["-f", "--format"])
def test_set_format_to_md(cli_runner, infile, option):
    txt = infile("sample.txt")
    output = cli_runner(option, "md", txt)
    assert "Generate Markdown file:" in output.stdout


@pytest.mark.parametrize("option", ["-f", "--format"])
def test_set_format_to_gmi(cli_runner, infile, option):
    txt = infile("sample.txt")
    output = cli_runner(option, "gmi", txt)
    assert "Generate GemText file:" in output.stdout


@pytest.mark.parametrize("option", ["-f", "--format"])
def test_set_format_to_typ(cli_runner, infile, option):
    txt = infile("sample.txt")
    output = cli_runner(option, "typ", txt)
    assert "Generate Typst file:" in output.stdout
