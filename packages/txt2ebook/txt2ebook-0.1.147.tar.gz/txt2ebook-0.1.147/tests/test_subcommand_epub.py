# pylint: disable=C0114,C0116

import pytest
from ebooklib import epub


def test_generate_epub(tte, infile, outfile):
    txtfile = infile("sample.txt")
    epubfile = outfile("output/sample.epub")

    output = tte("-l", "zh-cn", "epub", txtfile, epubfile)
    assert "" in output.stdout

    book = epub.read_epub(epubfile)

    assert book.get_metadata("DC", "creator") == [("李白", {"id": "creator"})]
    assert book.get_metadata("DC", "contributor") == []
    assert book.get_metadata("DC", "publisher") == []
    assert book.get_metadata("DC", "rights") == []
    assert book.get_metadata("DC", "coverage") == []
    assert book.get_metadata("DC", "date") == []
    assert book.get_metadata("DC", "description") == []
    assert book.get_metadata("DC", "title") == [("月下独酌·其一", {})]


@pytest.mark.parametrize("option", ["-et", "--epub-template"])
def test_unknown_epub_template(tte, infile, option):
    txtfile = infile("sample.txt")
    output = tte("epub", txtfile, option, "unknown")
    assert (
        "error: argument -et/--epub-template: invalid choice: 'unknown'"
        in output.stderr
    )
