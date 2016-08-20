import random
import re
import string

from mongoframes.factory.makers import Faker, Maker

__all__ = [
    'Code',
    'Join',
    'Lorem',
    'Markov'
    'Sequence'
    ]


class Code(Maker):
    """
    Generate a random code of the given length using either the default_charset
    or optionally a custom charset.
    """

    # The default character set that codes are made from
    default_charset = string.ascii_uppercase + string.digits

    def __init__(self, length, charset=None):
        super().__init__()

        # If no charset is provided use the default
        if not charset:
            charset = self.default_charset

        # The length of the code that will be generated
        self._length = length

        # The character set the code will be made from
        self._charset = list(charset)

    def _assemble(self):
        return ''.join([
            random.choice(self._charset) for i in range(0, int(self._length))
            ])


class Join(Maker):
    """
    Join the output of 2 or more items (makers and/or values) together with a
    seperator string.
    """

    def __init__(self, items, sep=' '):
        super().__init__()

        # The list of makers/values that will be joined
        self._items = items

        # The string used to join the items together
        self._sep = sep

    def _assemble(self):
        values = []
        for item in self._items:
            if isinstance(item, Maker):
                values.append(item._assemble())
            else:
                values.append(item)
        return values

    def _finish(self, value):
        parts = []
        for i, item in enumerate(self._items):
            if isinstance(item, Maker):
                parts.append(str(item._finish(value[i])))
            else:
                parts.append(str(item))
        return self._sep.join(parts)


class Lorem(Maker):
    """
    Generate random amounts of lorem ipsum.

    To determine the amount of text generated the type of text structure to
    generate must be specified;

    - body,
    - paragraph,
    - sentence

    along with the quantity;

    - paragraphs in a body,
    - sentences in a paragraph,
    - words in a scentence.
    """

    def __init__(self, text_type, quantity):
        super().__init__()

        # The type of text structure to generate
        self._text_type = text_type

        # The quantity of text to generate
        self._quantity = quantity

        assert self._text_type in ['body', 'paragraph', 'sentence'], \
                'Not a supported text type'

    def _assemble(self):
        quantity = int(self._quantity)

        if self._text_type == 'body':
            return '\n'.join(Faker.get_fake().paragraphs(nb=quantity))

        if self._text_type == 'paragraph':
            return Faker.get_fake().paragraph(
                nb_sentences=quantity,
                variable_nb_sentences=False
                )

        if self._text_type == 'sentence':
            return Faker.get_fake().sentence(
                nb_words=quantity,
                variable_nb_words=False
                )


class Markov(Maker):
    """
    Generate random amounts of text using a Markov chain.

    To determine the amount of text generated the type of text structure to
    generate must be specified;

    - body,
    - paragraph,
    - sentence

    along with the quantity;

    - paragraphs in a body,
    - sentences in a paragraph,
    - words in a sentence.

    This code is heavily based on (lifted from) the code presented in this
    article by Shabda Raaj:
    http://agiliq.com/blog/2009/06/generating-pseudo-random-text-with-markov-chains-u/
    """

    # FIXME:
    #   w1, w2 = w2, random.choice(db['freqs'][(w1, w2)])
    #   KeyError: ('summer...."\n\nTHE', 'END')

    _dbs = {}

    def __init__(self, db, text_type, quantity):
        super().__init__()

        # The database to generate the text from
        self._db = db

        assert db in self.__class__._dbs, 'Word database does not exist'

        # The type of text structure to generate
        self._text_type = text_type

        # The quantity of text to generate
        self._quantity = quantity

        assert self._text_type in ['body', 'paragraph', 'sentence'], \
                'Not a supported text type'

    # Public methds

    @property
    def database(self):
        """Return the selected word database"""
        return self.__class__._dbs[self._db]

    # Private methods

    def _assemble(self):
        quantity = int(self._quantity)

        if self._text_type == 'body':
            return self._body(quantity)

        if self._text_type == 'paragraph':
            return self._paragraph(quantity)

        if self._text_type == 'sentence':
            return self._sentence(quantity)

    def _body(self, paragraphs):
        """Generate a body of text"""
        body = []
        for i in range(paragraphs):
            paragraph = self._paragraph(random.randint(1, 10))
            body.append(paragraph)

        return '\n'.join(body)

    def _paragraph(self, sentences):
        """Generate a paragraph"""
        paragraph = []
        for i in range(sentences):
            sentence = self._sentence(random.randint(5, 16))
            paragraph.append(sentence)

        return ' '.join(paragraph)

    def _sentence(self, words):
        """Generate a sentence"""
        db = self.database

        # Generate 2 words to start a sentence with
        seed = random.randint(0, db['word_count'] - 3)
        seed_word, next_word = db['words'][seed], db['words'][seed + 1]
        w1, w2 = seed_word, next_word

        # Generate the complete sentence
        sentence = []
        for i in range(0, words - 1):
            sentence.append(w1)
            w1, w2 = w2, random.choice(db['freqs'][(w1, w2)])
        sentence.append(w2)

        # Make the sentence respectable
        sentence = ' '.join(sentence)

        # Capitalize the sentence
        sentence = sentence.capitalize()

        # Remove additional sentence ending puntuation
        sentence = sentence.replace('.', '')
        sentence = sentence.replace('!', '')
        sentence = sentence.replace('?', '')
        sentence = sentence.replace(':', '')

        # Remove quote tags
        sentence = sentence.replace('.', '')
        sentence = sentence.replace('!', '')
        sentence = sentence.replace('?', '')
        sentence = sentence.replace(':', '')
        sentence = sentence.replace('"', '')

        # If the last character is not an alphanumeric remove it
        sentence = re.sub('[^a-zA-Z0-9]$', '', sentence)

        # Remove excess space
        sentence = re.sub('\s+', ' ', sentence)

        # Add a full stop
        sentence += '.'

        return sentence

    @classmethod
    def init_word_db(cls, name, text):
        """Initialize a database of words for the maker with the given name"""
        # Prep the words
        text = text.replace('\n', ' ').replace('\r', ' ')
        words = [w.strip() for w in text.split(' ') if w.strip()]

        assert len(words) > 2, \
                'Database text sources must contain 3 or more words.'

        # Build the database
        freqs = {}
        for i in range(len(words) - 2):

            # Create a triplet from the current word
            w1 = words[i]
            w2 = words[i + 1]
            w3 = words[i + 2]

            # Add the triplet to the database
            key = (w1, w2)
            if key in freqs:
                freqs[key].append(w3)
            else:
                freqs[key] = [w3]

        # Store the database so it can be used
        cls._dbs[name] = {
            'freqs': freqs,
            'words': words,
            'word_count': len(words) - 2
            }


class Sequence(Maker):
    """
    Generate a sequence of values where a number is inserted into a template.
    The template should specify an index value, for example:

        "prefix-{index}"
    """

    def __init__(self, template, start_from=1):
        super().__init__()

        self._template = template
        self._start_from = start_from
        self._index = start_from

    def reset(self):
        self._index = self._start_from

    def _assemble(self):
        value = self._template.format(index=self._index)
        self._index += 1
        return value