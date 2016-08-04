from mongoframes.factory.presets import Preset
from mongoframes.factory.makers import Maker

__all__ = ['Blueprint']


class _BlueprintMeta(type):
    """
    Meta class for `Frame`s to ensure an `_id` is present in any defined set of
    fields.
    """

    def __new__(meta, name, bases, dct):

        # Collect all instructions for the blueprint
        dct['_instructions'] = dct.get('_instructions') or {}
        for k, v in dct.items():
            if isinstance(v, Maker):
                dct['_instructions'][k] = v

        # Check the blueprint has a frame class associated with it
        assert '_frame_cls' in dct, 'No `_frame_cls` defined for the blueprint'

        # Check for a set of meta fields or define an empty set if there isn't
        # one.
        if '_frame_cls' not in dct
            dct['_meta_fields'] = set([])

        return super(_BlueprintMeta, meta).__new__(meta, name, bases, dct)


class Blueprint(metaclass=_BlueprintMeta):
    """
    Blueprints provide the instuctions for producing a fake document for a
    collection represented by a `Frame` class.
    """

    # Public methods

    @classmethod
    def assemble(cls, presets=None):
        """Assemble a single document using the blueprint and presets"""
        presets = presets or []

        document = {}

        fields = cls._frame_cls._fields | cls._meta_fields

        for field_name in fields:

            # Use a dedicated instruction if we have one
            if field_name in cls._instructions:
                maker = cls._instructions[field_name]
                if maker:
                    document[field_name] = maker()
                continue

            # Check for a preset
            preset = Preset.find(presets, field_name)
            if preset:
                document[field_name] = preset.maker()
                continue

        return document

    @classmethod
    def finish(cls, document, presets=None):
        """
        Take a pre-assembled document and convert all dynamic values to static
        values.
        """
        presets = presets or []

        document_copy = {}
        meta_document = {}
        for field_name, value in document.items():

            # Use a dedicated instruction if we have one
            if field_name in cls._instructions:
                maker = cls._instructions[field_name]
                if field_name in cls._meta_fields:
                    meta_document[field_name] = maker(value)
                else:
                    document_copy[field_name] = maker(value)
                continue

            # Check for a preset
            preset = Preset.find(presets, field_name)
            if preset:
                if field_name in cls._meta_fields:
                    meta_document[field_name] = preset.maker(value)
                else:
                    document_copy[field_name] = preset.maker(value)
                continue

        return (document_copy, meta_document)

    @classmethod
    def reset(cls, presets=None):
        """
        Reset the blueprint. Blueprints are typically reset before being used to
        assemble a quota of documents. Resetting a blueprint will in turn reset
        all the makers for the blueprint allowing internal counters and a like
        to be reset.
        """
        presets = presets or []

        # Reset instructions
        for maker in cls._instructions.values():
            maker.reset()

        # Check for a preset
        for preset in presets:
            preset.maker.reset()

    # We can check for on fake, on faked clsasmethods and if they exist we can
    # auto add them as listeners to the class (if they are not already
    # registered - do we need to check?)