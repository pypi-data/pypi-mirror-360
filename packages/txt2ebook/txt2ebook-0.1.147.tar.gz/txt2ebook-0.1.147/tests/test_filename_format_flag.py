# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-ff", "--filename-format"])
def test_title_author_filename_format(cli_runner, infile, outfile, option):
    txt = infile("sample_with_metadata.txt")
    epub = outfile("scripttest/output/月下独酌·其一_李白.epub")
    output = cli_runner(txt, option, "1")
    assert f"Generate EPUB file: {epub}" in output.stdout

    out_txt = outfile("scripttest/output/月下独酌·其一_李白.txt")
    output = cli_runner(txt, "-f", "txt", option, "1")
    assert f"Generate TXT file: {out_txt}" in output.stdout


@pytest.mark.parametrize("option", ["-ff", "--filename-format"])
def test_author_title_filename_format(cli_runner, infile, outfile, option):
    txt = infile("sample_with_metadata.txt")
    epub = outfile("scripttest/output/李白_月下独酌·其一.epub")
    output = cli_runner(txt, option, "2")
    assert f"Generate EPUB file: {epub}" in output.stdout

    out_txt = outfile("scripttest/output/李白_月下独酌·其一.txt")
    output = cli_runner(txt, "-f", "txt", option, "2")
    assert f"Generate TXT file: {out_txt}" in output.stdout


@pytest.mark.parametrize("option", ["-ff", "--filename-format"])
def test_raise_error_on_invalid_filename_format(cli_runner, infile, option):
    txt = infile("sample_with_metadata.txt")
    output = cli_runner(txt, option, "3")
    assert "invalid filename format: '3'!" in output.stdout
