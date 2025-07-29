# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-tr", "--translator"])
def test_set_single_translator(cli_runner, option, infile):
    txtfile = infile("sample.txt")
    output = cli_runner(txtfile, "-d", option, "foobar")
    assert "translator=['foobar']" in output.stdout


@pytest.mark.parametrize("option", ["-tr", "--translator"])
def test_set_multiple_translators(cli_runner, option, infile):
    txtfile = infile("sample.txt")
    output = cli_runner(txtfile, "-d", option, "foo", option, "bar")
    assert "translator=['foo', 'bar']" in output.stdout
