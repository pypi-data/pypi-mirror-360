# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-p", "--purge"])
def test_debug_log(cli_runner, infile, option):
    txt = infile("sample.txt")
    output = cli_runner(txt, "-d", option)
    assert "purge=True" in output.stdout


def test_purge_output_folder_if_exists(cli_runner, infile, tmpdir):
    csv = infile("sample.txt")
    opf = f"{tmpdir}/output"
    _ = cli_runner(csv, "-d", "-of", opf)
    output = cli_runner(csv, "-d", "-of", opf, "-p", "-y")
    assert f"Purge output folder: {opf}" in output.stdout


def test_prompt_when_purging_output_folder(cli_runner, infile, tmpdir):
    csv = infile("sample.txt")
    opf = f"{tmpdir}/output"
    _ = cli_runner(csv, "-d", "-of", opf)

    output = cli_runner(csv, "-d", "-of", opf, "-p", stdin=b"y")
    assert (
        f"Are you sure to purge output folder: {opf}? [y/N] " in output.stdout
    )


def test_no_purge_output_folder_if_not_exists(cli_runner, infile):
    csv = infile("sample.txt")
    output_folder = csv.resolve().parent.joinpath("output")
    output = cli_runner(csv, "-d", "-p")
    assert f"Purge output folder: {output_folder}" not in output.stdout
