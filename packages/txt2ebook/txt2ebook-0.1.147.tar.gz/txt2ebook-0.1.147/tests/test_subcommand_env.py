# pylint: disable=C0114,C0116

from txt2ebook import __version__


def test_env_output(tte):
    output = tte("env")
    assert f"txt2ebook: {__version__}" in output.stdout
    assert "python: " in output.stdout
    assert "platform: " in output.stdout
