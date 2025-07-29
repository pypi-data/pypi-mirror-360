# pylint: disable=C0114,C0116

import pytest

from txt2ebook.zh_utils import zh_numeric


def test_delegate_to_unicodedata_numeric():
    expects = {
        "零": 0.0,
        "五": 5.0,
        "十": 10.0,
        "廿": 20.0,
        "卅": 30.0,
        "卌": 40.0,
    }
    for word, value in expects.items():
        assert zh_numeric(word) == value


def test_custome_numeral_values():
    expects = {
        "圩": 50.0,
        "圓": 60.0,
        "進": 70.0,
        "枯": 80.0,
        "枠": 90.0,
    }
    for word, value in expects.items():
        assert zh_numeric(word) == value


def test_raise_exception_for_not_a_numeric_character():
    msg = r"not a numeric character"
    with pytest.raises(ValueError, match=msg):
        zh_numeric("道")


def test_raise_exception_for_string():
    msg = r"zh_numeric\(\) argument 1 must be a unicode character, not str"
    with pytest.raises(TypeError, match=msg):
        zh_numeric("照見五蘊皆空")


def test_for_default():
    assert zh_numeric("道", 0.0) == 0.0
