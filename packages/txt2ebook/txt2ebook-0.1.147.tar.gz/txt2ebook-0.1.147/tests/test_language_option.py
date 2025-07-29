# pylint: disable=C0114,C0116

import pytest


def test_auto_detect_language(cli_runner, infile):
    txtfile = infile("sample.txt")
    output = cli_runner(txtfile)
    assert "Detect language: zh-cn" in output.stdout


@pytest.mark.parametrize("option", ["-l", "--language"])
def test_warning_log_for_mismatch_configured_and_detect_language(
    cli_runner, infile, option
):
    txtfile = infile("missing_chapters.txt")
    output = cli_runner(txtfile, option, "en")
    assert "Config language: en" in output.stdout
    assert "Detect language: ko" in output.stdout
    assert "Config (en) and detect (ko) language mismatch" in output.stdout
