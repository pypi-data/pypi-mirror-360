# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-vp", "--volume-page"])
def test_logging(cli_runner, infile, option):
    txtfile = infile("sample_all_headers.txt")
    output = cli_runner("-d", option, txtfile)
    assert "Create separate volume page: " in output.stdout
