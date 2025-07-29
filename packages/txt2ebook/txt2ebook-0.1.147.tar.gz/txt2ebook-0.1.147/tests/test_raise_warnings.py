# pylint: disable=C0114,C0116


def test_empty_line_before_chapter_header(cli_runner, infile):
    txtfile = infile("sample_with_issues.txt")
    output = cli_runner("-d", "-rw", txtfile)

    assert (
        "ERROR: Found newline before chapter header: '\\n第2章 影徒随我身'"
        in output.stdout
    )
