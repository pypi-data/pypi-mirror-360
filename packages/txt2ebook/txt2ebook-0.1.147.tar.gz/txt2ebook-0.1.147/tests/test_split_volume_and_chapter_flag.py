# pylint: disable=C0114,C0116

from pathlib import Path

import pytest


@pytest.mark.parametrize("option", ["-sp", "--split-volume-and-chapter"])
def test_logging_of_split_text_files(cli_runner, infile, tmpdir, option):
    txtfile = infile("sample_all_headers.txt")
    output = cli_runner("-f", "txt", "-d", option, txtfile)

    logs = [
        f"INFO: Creating {tmpdir}/output/00_sample_all_headers_元数据.txt",
        f"INFO: Creating {tmpdir}/output/01_00_sample_all_headers_第一卷_第1章_月既不解饮.txt",
        f"INFO: Creating {tmpdir}/output/01_01_sample_all_headers_第一卷_第2章_影徒随我身.txt",
        f"INFO: Creating {tmpdir}/output/02_00_sample_all_headers_第二卷_第3章_暂伴月将影.txt",
    ]
    for log in logs:
        assert log in output.stdout


@pytest.mark.parametrize("option", ["-sp", "--split-volume-and-chapter"])
def test_split_filenames_by_sequence_volume_chapter(
    cli_runner, infile, tmpdir, option
):
    txtfile = infile("sample_all_headers.txt")
    cli_runner("-f", "txt", "-d", option, txtfile)

    files = [
        f"{tmpdir}/output/00_sample_all_headers_元数据.txt",
        f"{tmpdir}/output/01_00_sample_all_headers_第一卷_第1章_月既不解饮.txt",
        f"{tmpdir}/output/01_01_sample_all_headers_第一卷_第2章_影徒随我身.txt",
        f"{tmpdir}/output/02_00_sample_all_headers_第二卷_第3章_暂伴月将影.txt",
    ]

    for file in files:
        assert Path(file).exists()
