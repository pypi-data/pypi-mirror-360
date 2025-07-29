# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-ow", "--overwrite"])
def test_overwrite_source_txt_file(cli_runner, infile, option):
    txtfile = infile("sample.txt")
    output = cli_runner(txtfile, option)
    assert "Backup txt file" not in output.stdout
