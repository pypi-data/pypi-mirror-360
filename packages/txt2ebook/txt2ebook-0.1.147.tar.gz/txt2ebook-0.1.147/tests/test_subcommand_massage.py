# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-rl", "--regex-delete-line"])
def test_delete_line_regex(tte, infile, option):
    txtfile = infile("sample.txt")
    tte("massage", txtfile, "-ow", option, "我歌月徘徊")

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        assert "我歌月徘徊" not in content


@pytest.mark.parametrize("option", ["-rr", "--regex-replace"])
def test_single_replace_regex(tte, infile, option):
    txtfile = infile("sample.txt")

    tte("massage", txtfile, "-ow", option, "章", "章:")

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        assert "第1章:" in content
        assert "第2章:" in content
        assert "第3章:" in content


@pytest.mark.parametrize("option", ["-rd", "--regex-delete"])
def test_single_delete_regex(tte, infile, option):
    txtfile = infile("sample.txt")
    tte("massage", txtfile, "-ow", option, "歌月", option, "我")

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        assert "徘徊，舞影零乱。" in content


@pytest.mark.parametrize("option", ["-fw", "--fullwidth"])
def test_fullwidth(tte, infile, option):
    txtfile = infile("sample.txt")
    tte("massage", txtfile, "-ow", option)

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        # Check for conversion of halfwidth characters
        assert "１２３" in content
        assert "ＡＢＣ" in content
        assert "！＠＃＄" in content


@pytest.mark.parametrize("option", ["-sn", "--single-newline"])
def test_single_newline(tte, infile, option):
    txtfile = infile("sample.txt")
    tte("massage", txtfile, "-ow", option)

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        # Check that multiple newlines are reduced to single newlines between paragraphs
        assert "This paragraph has\n\nmultiple newlines" in content
        assert "between lines.\n\nThis is a very long line" in content
        # Ensure single newlines within a paragraph are preserved by wrapping logic
        # (though single_newline runs before wrapping, the effect is tested here)
        assert (
            "花间一壶酒，独酌无相亲。\n\n举杯邀明月，对影成三人。" in content
        )


@pytest.mark.parametrize("option", ["-w", "--width"])
def test_width(tte, infile, option):
    txtfile = infile("sample.txt")
    # Use a small width to force wrapping
    tte("massage", txtfile, "-ow", option, "40")

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        # Check that the long line is wrapped
        long_line_wrapped = "This is a very long line that should be\nwrapped when a width is specified. It needs\nto be long enough to exceed the typical\ndefault width and force wrapping. Let's\nmake it even longer to be sure. This is a\nvery long line that should be wrapped when\na width is specified. It needs to be long\nenough to exceed the typical default width\nand force wrapping. Let's make it even\nlonger to be sure."
        assert long_line_wrapped in content


@pytest.mark.parametrize("option", ["-ps", "--paragraph_separator"])
def test_paragraph_separator(tte, infile, option):
    txtfile = infile("sample.txt")
    separator = "<br>"
    tte("massage", txtfile, "-ow", option, separator)

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        # Check that the custom separator is used between paragraphs
        assert (
            "花间一壶酒，独酌无相亲。" + separator + "举杯邀明月，对影成三人。"
            in content
        )
        assert (
            "between lines." + separator + "This is a very long line"
            in content
        )


def test_multiple_regex(tte, infile):
    txtfile = infile("sample.txt")
    # Apply multiple regex options
    tte(
        "massage",
        txtfile,
        "-ow",
        "-rl",
        "我歌月徘徊",  # Delete line
        "-rr",
        "章",
        "章:",  # Replace
        "-rd",
        "无相亲",  # Delete word/phrase
    )

    with open(txtfile, encoding="utf8") as file:
        content = file.read()
        # Check all regex effects
        assert "我歌月徘徊" not in content  # Line deleted
        assert "第1章:" in content  # Replace applied
        assert "独酌无相亲" not in content  # Word/phrase deleted
        assert (
            "花间一壶酒，独酌。" in content
        )  # Check surrounding text after deletion
