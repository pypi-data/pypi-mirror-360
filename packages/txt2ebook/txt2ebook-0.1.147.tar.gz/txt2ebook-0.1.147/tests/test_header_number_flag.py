# pylint: disable=C0114,C0116

from textwrap import dedent

import pytest


@pytest.mark.parametrize("option", ["-hn", "--header-number"])
def test_header_to_numbers_conversion(cli_runner, infile, option):
    txtfile = infile("sample_long_headers.txt")

    output = cli_runner("-d", option, txtfile)
    expected_output1 = dedent(
        """\
        DEBUG: Convert header to numbers: 第一卷 -> 第1卷
        DEBUG: Convert header to numbers: 第一章 月既不解饮 -> 第1章 月既不解饮
        DEBUG: Convert header to numbers: 第二章 影徒随我身 -> 第2章 影徒随我身
    """
    )
    assert expected_output1 in output.stdout

    output = cli_runner("-d", "--header-number", txtfile)
    expected_output2 = dedent(
        """\
        DEBUG: Convert header to numbers: 第二卷 -> 第2卷
        DEBUG: Convert header to numbers: 第三章 暂伴月将影 -> 第3章 暂伴月将影
        DEBUG: Convert header to numbers: 第二百章 暂伴月将影 -> 第200章 暂伴月将
        DEBUG: Convert header to numbers: 第九百九十九章 暂伴 -> 第999章 暂伴月将
        DEBUG: Convert header to numbers: 第九千百九十九章 暂 -> 第9919章 暂伴月
    """
    )

    assert expected_output2 in output.stdout
