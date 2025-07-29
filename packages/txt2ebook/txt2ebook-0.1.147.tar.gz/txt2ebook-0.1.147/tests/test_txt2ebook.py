# pylint: disable=C0114,C0116

from txt2ebook import __version__


def test_version(tte):
    output = tte("--version")
    assert f"txt2ebook {__version__}" in output.stdout
