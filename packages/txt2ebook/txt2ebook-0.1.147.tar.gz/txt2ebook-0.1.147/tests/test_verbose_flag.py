# pylint: disable=C0114,C0116,line-too-long

from textwrap import dedent


def test_default_verbosity(cli_runner, infile):
    txtfile = infile("sample_all_headers.txt")

    output = cli_runner("-d", txtfile)
    assert (
        dedent(
            """\
    DEBUG: Volume(title='第一卷', chapters='2')
    DEBUG: Chapter(title='第1章 月既不解饮', paragraphs='2')
    DEBUG: Chapter(title='第2章 影徒随我身', paragraphs='1')
    DEBUG: Volume(title='第二卷', chapters='1')
    DEBUG: Chapter(title='第3章 暂伴月将影', paragraphs='1')
    """
        )
        not in output.stdout
    )

    output = cli_runner("-d", "-v", txtfile)
    assert (
        dedent(
            """\
    DEBUG: Volume(title='第一卷', chapters='2')
    DEBUG: Chapter(title='第1章 月既不解饮', paragraphs='2')
    DEBUG: Chapter(title='第2章 影徒随我身', paragraphs='1')
    DEBUG: Volume(title='第二卷', chapters='1')
    DEBUG: Chapter(title='第3章 暂伴月将影', paragraphs='1')
    """
        )
        not in output.stdout
    )


def test_second_level_verbosity(cli_runner, infile):
    txtfile = infile("sample_all_headers.txt")

    output = cli_runner("-d", "-vv", txtfile)
    assert (
        dedent(
            """\
    DEBUG: Volume(title='第一卷', chapters='2')
    DEBUG: Chapter(title='第1章 月既不解饮', paragraphs='2')
    DEBUG: Chapter(title='第2章 影徒随我身', paragraphs='1')
    DEBUG: Volume(title='第二卷', chapters='1')
    DEBUG: Chapter(title='第3章 暂伴月将影', paragraphs='1')
    """
        )
        in output.stdout
    )


def test_third_level_verbosity(cli_runner, infile):
    txtfile = infile("sample_all_headers.txt")

    output = cli_runner("-d", "-vvv", txtfile)
    assert (
        dedent(
            """\
    DEBUG: Token stats: Counter({'PARAGRAPH': 5, 'CHAPTER': 3, 'VOLUME': 2, 'TITLE': 1, 'AUTHOR': 1})
    DEBUG: Token(type='TITLE', line_no='0', value='月下独酌·其一')
    DEBUG: Token(type='AUTHOR', line_no='6', value='李白')
    DEBUG: Token(type='PARAGRAPH', line_no='6', value='李白')
    DEBUG: Token(type='VOLUME', line_no='8', value='第一卷')
    DEBUG: Token(type='CHAPTER', line_no='10', value='第1章 月既不解饮')
    DEBUG: Token(type='PARAGRAPH', line_no='12', value='花间一壶酒，独酌无相')
    DEBUG: Token(type='PARAGRAPH', line_no='29', value='我歌月徘徊，我舞影零')
    DEBUG: Token(type='CHAPTER', line_no='19', value='第2章 影徒随我身')
    DEBUG: Token(type='PARAGRAPH', line_no='29', value='我歌月徘徊，我舞影零')
    DEBUG: Token(type='VOLUME', line_no='25', value='第二卷')
    DEBUG: Token(type='CHAPTER', line_no='27', value='第3章 暂伴月将影')
    DEBUG: Token(type='PARAGRAPH', line_no='29', value='我歌月徘徊，我舞影零')
    """
        )
        in output.stdout
    )
