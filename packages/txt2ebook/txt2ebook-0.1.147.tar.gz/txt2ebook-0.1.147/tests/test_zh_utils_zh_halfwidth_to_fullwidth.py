# pylint: disable=C0114,C0116


from txt2ebook.zh_utils import zh_halfwidth_to_fullwidth


def test_halfwidth_to_fullwidth():
    assert zh_halfwidth_to_fullwidth(":") == "："
