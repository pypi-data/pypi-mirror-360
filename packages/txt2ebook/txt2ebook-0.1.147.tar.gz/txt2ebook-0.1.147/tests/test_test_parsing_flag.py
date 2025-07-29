# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-tp", "--test-parsing"])
def test_show_chapter_headers_only(cli_runner, infile, option):
    txtfile = infile("sample.txt")
    output = cli_runner(txtfile, "-d", option)

    assert "EPUB CSS template" not in output.stdout
    assert "Generate EPUB file" not in output.stdout
    assert "Backup txt file" not in output.stdout
    assert "Overwrite txt file" not in output.stdout
    assert "Chapter(title='第一千九百二十四章" in output.stdout
