# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-q", "--quiet"])
def test_show_chapter_headers_only(cli_runner, infile, option):
    txtfile = infile("sample.txt")
    output = cli_runner(txtfile, option)

    assert output.stdout == ""
