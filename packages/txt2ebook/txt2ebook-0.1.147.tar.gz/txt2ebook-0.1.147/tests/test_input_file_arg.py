# pylint: disable=C0114,C0116


def test_nonexistent_filename(cli_runner):
    output = cli_runner("parse", "nonexistent.txt")
    assert (
        "[Errno 2] No such file or directory: 'nonexistent.txt'"
        in output.stderr
    )


def test_empty_file_content(cli_runner, infile):
    txt = infile("empty_file.txt")
    output = cli_runner("parse", str(txt))
    assert f"error: Empty file content in {str(txt)}" in output.stdout
