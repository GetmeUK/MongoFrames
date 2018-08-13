from blinker import signal
from collections import OrderedDict

from mongoframes.factory.makers import Maker

__all__ = ['Blueprint']


class _BlueprintMeta(type):
    """
    Meta class for `Frame`s to ensure an `_id` is present in any defined set of
    fields.
    """

    def __new__(meta, name, bases, dct):

        # Collect all instructions for the blueprint. Each instruction is stored
        # as a key value pair in a dictionary where the name represents the
        # field the instruction refers to and the value is a `Maker` type for
        # generating a value for that field.
        dct['_instructions'] = dct.get('_instructions') or {}

        # Ensure the instructions are an ordered dictionary
        dct['_instructions'] = OrderedDict(dct['_instructions'])

        for k, v in dct.items():
            if isinstance(v, Maker):
                dct['_instructions'][k] = v

        # Check the blueprint has a frame class associated with it. The `Frame`
        # class will be used to insert the document into the database.
        assert '_frame_cls' in dct or len(bases) == 0, \
                'No `_frame_cls` defined for the blueprint'

        # Check for a set of meta fields or define an empty set if there isn't
        # one. Meta-fields determine a set of one or more fields that should be
        # set when generating a document but which are not defined in the
        # assoicated `Frame` classes `_fields` attribute.
        if '_meta_fields' not in dct:
            dct['_meta_fields'] = set([])

        return super(_BlueprintMeta, meta).__new__(meta, name, bases, dct)


class Blueprint(metaclass=_BlueprintMeta):
    """
    Blueprints provide the instructions for producing a fake document for a
    collection represented by a `Frame` class.
    """

    def __init__(self):
        assert False, \
            'Blueprint classes should remain static and not be initialized'

    # Public methods

    @classmethod
    def get_frame_cls(cls):
        """Return the `Frame` class for the blueprint"""
        return cls._frame_cls

    @classmethod
    def get_instructions(cls):
        """Return the instructions for the blueprint"""
        return dict(cls._instructions)

    @classmethod
    def get_meta_fields(cls):
        """Return the meta-fields for the blueprint"""
        return cls._meta_fields

    # Factory methods

    @classmethod
    def assemble(cls):
        """Assemble a single document using the blueprint"""
        document = {}
        for field_name, maker in cls._instructions.items():
            with maker.target(document):
                document[field_name] = maker()
        return document

    @classmethod
    def finish(cls, document):
        """
        Take a assembled document and convert all assembled values to
        finished values.
        """
        target_document = {}
        document_copy = {}
        for field_name, value in document.items():
            maker = cls._instructions[field_name]
            target_document = document.copy()
            with maker.target(target_document):
                document_copy[field_name] = maker(value)
                target_document[field_name] = document_copy[field_name]
        return document_copy

    @classmethod
    def reassemble(cls, fields, document):
        """
        Take a previously assembled document and reassemble the given set of
        fields for it in place.
        """
        for field_name in cls._instructions:
            if field_name in fields:
                maker = cls._instructions[field_name]
                with maker.target(document):
                    document[field_name] = maker()

    @classmethod
    def reset(cls):
        """
        Reset the blueprint. Blueprints are typically reset before being used to
        assemble a quota of documents. Resetting a Blueprint will in turn reset
        all the Maker instances defined as instructions for the Blueprint
        allowing internal counters and alike to be reset.
        """
        # Reset instructions
        for maker in cls._instructions.values():
            maker.reset()

    # Events

    @classmethod
    def on_fake(cls, frames):
        """Called before frames are inserted"""

        # By default the hook will simply trigger a `fake` event against the
        # frame. This allows the overriding method to control this behaviour.
        signal('fake').send(cls._frame_cls, frames=frames)

    @classmethod
    def on_faked(cls, frames):
        """Called after frames are inserted"""

        # By default the hook will simply trigger a `fake` event against the
        # frame. This allows the overriding method to control this behaviour.
        signal('faked').send(cls._frame_cls, frames=frames)