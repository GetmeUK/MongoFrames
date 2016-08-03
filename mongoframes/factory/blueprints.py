from mongoframes.factory.presets import Preset

__all__ = ['Blueprint']


class Blueprint:
    """
    Blueprints provide the instuctions for producing a fake document for a
    collection represented by a `Frame` class.
    """

    def __init__(self, frame_cls, instructions=None, meta_fields=None):

        # The Frame class the blueprint is for
        self._frame_cls = frame_cls

        # A table of fields names mapped to makers
        self._instructions = instructions or {}

        # A set of meta fields names
        self._meta_fields = meta_fields or set([])

    # Read-only properties

    @property
    def frame_cls(self):
        return self._frame_cls

    # Public methods

    def assemble(self, presets=None):
        """Assemble a single document using the blueprint and presets"""
        presets = presets or []

        document = {}

        fields = self._frame_cls._fields | self._meta_fields

        for field_name in fields:

            # Use a dedicated instruction if we have one
            if field_name in self._instructions:
                maker = self._instructions[field_name]
                if maker:
                    document[field_name] = maker()
                continue

            # Check for a preset
            preset = Preset.find(presets, field_name)
            if preset:
                document[field_name] = preset.maker()
                continue

        return document

    def finish(self, document, presets=None):
        """
        Take a pre-assembled document and convert all dynamic values to static
        values.
        """
        presets = presets or []

        document_copy = {}
        meta_document = {}
        for field_name, value in document.items():

            # Use a dedicated instruction if we have one
            if field_name in self._instructions:
                maker = self._instructions[field_name]
                if field_name in self._meta_fields:
                    meta_document[field_name] = maker(value)
                else:
                    document_copy[field_name] = maker(value)
                continue

            # Check for a preset
            preset = Preset.find(presets, field_name)
            if preset:
                if field_name in self._meta_fields:
                    meta_document[field_name] = preset.maker(value)
                else:
                    document_copy[field_name] = preset.maker(value)
                continue

        return (document_copy, meta_document)

    def reset(self, presets=None):
        """
        Reset the blueprint. Blueprints are typically reset before being used to
        assemble a quota of documents. Resetting a blueprint will in turn reset
        all the makers for the blueprint allowing internal counters and a like
        to be reset.
        """
        presets = presets or []

        # Reset instructions
        for maker in self._instructions.values():
            maker.reset()

        # Check for a preset
        for preset in presets:
            preset.maker.reset()