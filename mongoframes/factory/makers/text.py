from mongoframes.factory.makers import Maker

__all__ = [
    'Lorem',
    'Sequence'
    ]


# @@
# - Nice text output


class Sequence(Maker):
    """
    Generate a sequence of values where a number is inserted into a template.
    The template should specify an index value, for example:

        "prefix-{index}"
    """

    def __init__(self, template, start_from=1):
        self._template = template
        self._index = start_from

    def _assemble(self):
        value = self._template.format(index=self._index)
        self._index += 1
        return value


class Lorem(Maker):
    """
    Generate random amounts of lorem ipsum.

    To determine the amount of lorem ipsum generated you need to specify the
    type of text structure to generate;

    - body,
    - paragraph,
    - sentence

    and then the quantity;

    - paragraphs in a body,
    - sentances in a paragraph,
    - words in a scentance.
    """

    def __init__(self, text_type, quantity):
        self._text_type = text_type
        self._quantity = quantity

        assert self._text_type in ['body', 'paragraph', 'sentence'], \
            'Not a supported text type'

    def _assemble(self):
        quantity = int(self._quantity)

        if self._text_type == 'body':
            return self.get_fake().paragraphs(nb=quantity)

        if self._text_type == 'paragraph':
            return self.get_fake().paragraphs(nb_sentences=quantity)

        if self._text_type == 'sentence':
            return self.get_fake().sentence(nb_words=quantity)