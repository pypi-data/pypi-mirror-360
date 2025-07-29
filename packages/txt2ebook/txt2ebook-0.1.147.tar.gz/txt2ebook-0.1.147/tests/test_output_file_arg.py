# pylint: disable=C0114,C0116


def test_output_basename_default_to_input_basename(
    cli_runner, infile, outfile
):
    txt = infile("sample.txt")
    epub = outfile("output/sample.epub")
    output = cli_runner(str(txt))

    assert epub.exists()
    assert f"Generate EPUB file: {str(epub)}" in output.stdout


def test_set_output_filename(cli_runner, infile, outfile):
    txt = infile("sample.txt")
    epub = outfile("foobar.epub")
    output = cli_runner(str(txt), str(epub))

    assert epub.exists()
    assert f"Generate EPUB file: {str(epub)}" in output.stdout
