# pylint: disable=C0114,C0116

from textwrap import dedent

import pytest


@pytest.mark.parametrize("option", ["-ss", "--sort-volume-and-chapter"])
def test_sort_logs(cli_runner, infile, option):
    txtfile = infile("sample_unsorted_headers.txt")

    output = cli_runner("-d", "-l", "zh-cn", "-vv", option, txtfile)
    assert (
        """
"""
        in output.stdout
    )

    assert (
        dedent(
            """\
    DEBUG: Chapter(title='序章', paragraphs='1')
    DEBUG: Volume(title='第一卷', chapters='1')
    DEBUG: Chapter(title='第3章 暂伴月将影', paragraphs='1')
    DEBUG: Volume(title='第二卷', chapters='2')
    DEBUG: Chapter(title='第1章 月既不解饮', paragraphs='1')
    DEBUG: Chapter(title='第2章 影徒随我身', paragraphs='2')
    """
        )
        in output.stdout
    )
