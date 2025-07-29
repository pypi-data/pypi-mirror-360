# pylint: disable=C0114,C0116
import argparse

import pytest

from txt2ebook.parser import Parser


@pytest.fixture(name="config")
def fixture_config():
    return argparse.Namespace(
        **{
            "author": False,
            "translator": False,
            "cover": None,
            "fullwidth": False,
            "header_number": False,
            "language": "zh-cn",
            "no_wrapping": False,
            "paragraph_separator": "\n\n",
            "raise_on_warning": False,
            "re_author": (),
            "re_chapter": (),
            "re_delete": False,
            "re_delete_line": False,
            "re_replace": False,
            "re_title": (),
            "re_volume": (),
            "re_volume_chapter": (),
            "sort_volume_and_chapter": False,
            "title": False,
            "verbose": 1,
            "width": False,
        }
    )


def test_parsing_two_newlines_as_paragraph_separator(config):
    content = """\
---
书名：月下独酌·其一
作者：李白
---

第一章

天地玄黄。(paragraph 1)

寒来暑往，秋收冬藏。(paragraph 2)
云腾致雨，露结为霜，金生丽水。(paragraph 2)

第二章

剑号巨阙，珠称夜光，果珍李柰，菜重芥姜。(paragraph 1)
"""
    parser = Parser(content, config)
    [chapter1, chapter2] = parser.parse().toc
    assert len(chapter1.paragraphs) == 2
    assert len(chapter2.paragraphs) == 1


def test_parsing_one_newline_as_paragraph_separator(config):
    content = """\
---
书名：月下独酌·其一
作者：李白
---

第一章
天地玄黄。(paragraph 1)
寒来暑往，秋收冬藏。 (paragraph 2)
云腾致雨，露结为霜，金生丽水。 (paragraph 3)
第二章
剑号巨阙，珠称夜光，果珍李柰，菜重芥姜。(paragraph 1)
"""
    config.paragraph_separator = "\n"
    parser = Parser(content, config)
    book = parser.parse()
    [chapter1, chapter2] = book.toc
    assert len(chapter1.paragraphs) == 3
    assert len(chapter2.paragraphs) == 1
