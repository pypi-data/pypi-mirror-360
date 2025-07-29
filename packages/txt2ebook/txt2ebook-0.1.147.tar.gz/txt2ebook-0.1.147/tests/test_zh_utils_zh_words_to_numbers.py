# pylint: disable=C0114,C0116

import pytest

from txt2ebook.zh_utils import zh_words_to_numbers


def test_words_to_numbers():
    assert zh_words_to_numbers("第一百零八章") == "第108章"
    assert zh_words_to_numbers("第一百零八章", length=5) == "第00108章"
    assert zh_words_to_numbers("第两千一百零八章") == "第2108章"
    assert zh_words_to_numbers("第章") == "第章"


def test_convert_first_found_words_only_by_default():
    assert zh_words_to_numbers("第一百零八章 第一百章") == "第108章 第一百章"
    assert (
        zh_words_to_numbers("第一百零八章 第一百章", match_all=True)
        == "第108章 第100章"
    )


def test_warning_for_invalid_prepend_length_to_word():
    regex = (
        "prepend zero length less than word length, "
        r"word length: \d+, prepend length: \d+"
    )
    with pytest.warns(UserWarning, match=rf"{regex}"):
        zh_words_to_numbers("第一百零八章", length=1)
