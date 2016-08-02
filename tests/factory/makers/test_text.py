from mongoframes.factory import makers
from mongoframes.factory import quotas
from mongoframes.factory.makers import text as text_makers


def test_code():
    """`Code` makers should return a random code"""

    # Configured with the default character set
    maker = text_makers.Code(quotas.Quota(4))

    # Check the assembled result
    assembled = maker._assemble()
    assert len(assembled) == 4
    assert set(assembled).issubset(set(maker.default_charset))

    # Check the finished result
    finished = maker._finish(assembled)
    assert len(finished) == 4
    assert set(assembled).issubset(set(maker.default_charset))

    # Configured with a custom charset
    custom_charset = 'ABCDEF1234567890'
    maker = text_makers.Code(quotas.Quota(6), custom_charset)

    # Check the assembled result
    assembled = maker._assemble()
    assert len(assembled) == 6
    assert set(assembled).issubset(set(custom_charset))

    # Check the finished result
    finished = maker._finish(assembled)
    assert len(finished) == 6
    assert set(assembled).issubset(set(custom_charset))

def test_join():
    """
    `Join` makers should return a the value of one or more items (python strings
    or makers) joined together.
    """

    # Configured with a list of python strings
    maker = text_makers.Join(['foo', 'bar', 'zee'])

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == ['foo', 'bar', 'zee']

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 'foo bar zee'

    # Configured with a list of makers
    maker = text_makers.Join([
        makers.Static('foo'),
        makers.Static('bar'),
        makers.Static('zee')
        ])

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == ['foo', 'bar', 'zee']

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 'foo bar zee'

    # Configured with a custom separator
    maker = text_makers.Join(['foo', 'bar', 'zee'], '-')

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == ['foo', 'bar', 'zee']

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 'foo-bar-zee'

def test_lorem():
    """`Lorem` makers should return lorem ipsum"""

    # Configured to return a body of text
    maker = text_makers.Lorem('body', quotas.Quota(5))

    # Check the assembled result
    assembled = maker._assemble()
    assert len(assembled.split('\n')) == 5

    # Check the finished result
    finished = maker._finish(assembled)
    assert len(finished.split('\n')) == 5

    # Configured to return a paragraph
    maker = text_makers.Lorem('paragraph', quotas.Quota(5))

    # Check the assembled result
    assembled = maker._assemble()
    paragraphs = [p for p in assembled.split('.') if p.strip()]
    assert len(paragraphs) == 5

    # Check the finished result
    finished = maker._finish(assembled)
    paragraphs = [p for p in finished.split('.') if p.strip()]
    assert len(paragraphs) == 5

    # Configured to return a sentence
    maker = text_makers.Lorem('sentence', quotas.Quota(5))

    # Check the assembled result
    assembled = maker._assemble()
    words = [w for w in assembled.split(' ') if w.strip()]
    assert len(words) == 5

    # Check the finished result
    finished = maker._finish(assembled)
    words = [w for w in finished.split(' ') if w.strip()]
    assert len(words) == 5

def test_markov():
    """`Markov` makers should return random text built from a text body"""

    # Set up markov word database
    with open('tests/factory/data/markov.txt') as f:
        text_makers.Markov.init_word_db('test', f.read())

    # Configured to return a body of text
    maker = text_makers.Markov('test', 'body', quotas.Quota(5))

    # Check the assembled result
    assembled = maker._assemble()
    assert len(assembled.split('\n')) == 5

    # Check the finished result
    finished = maker._finish(assembled)
    assert len(finished.split('\n')) == 5

    # Configured to return a paragraph
    maker = text_makers.Markov('test', 'paragraph', quotas.Quota(5))

    # Check the assembled result
    assembled = maker._assemble()
    paragraphs = [p for p in assembled.split('.') if p.strip()]
    assert len(paragraphs) == 5

    # Check the finished result
    finished = maker._finish(assembled)
    paragraphs = [p for p in finished.split('.') if p.strip()]
    assert len(paragraphs) == 5

    # Configured to return a sentence
    maker = text_makers.Markov('test', 'sentence', quotas.Quota(5))

    # Check the assembled result
    assembled = maker._assemble()
    words = [w for w in assembled.split(' ') if w.strip()]
    assert len(words) == 5

    # Check the finished result
    finished = maker._finish(assembled)
    words = [w for w in finished.split(' ') if w.strip()]
    assert len(words) == 5

def test_sequence():
    """
    `Sequence` makers should generate a sequence of strings containing a
    sequence of numbers.
    """

    # Configured with the defaut start from
    maker = text_makers.Sequence('foo-{index}')

    for i in range(0, 10):

        # Check the assembled result
        assembled = maker._assemble()
        assert assembled == 'foo-{index}'.format(index=i + 1)

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == 'foo-{index}'.format(index=i + 1)

    # Configured with a custom start from
    maker = text_makers.Sequence('foo-{index}', 5)

    for i in range(0, 10):

        # Check the assembled result
        assembled = maker._assemble()
        assert assembled == 'foo-{index}'.format(index=i + 5)

        # Check the finished result
        finished = maker._finish(assembled)
        assert finished == 'foo-{index}'.format(index=i + 5)

    # Reset should reset the sequence to start from
    maker.reset()

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == 'foo-5'

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 'foo-5'