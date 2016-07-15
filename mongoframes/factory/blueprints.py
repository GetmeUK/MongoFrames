from .presets import Preset

__all__ = ['Blueprint']


class Blueprint:
    """
    Blueprints provide the instuctions for producing a fake document for a
    collection represented by a `Frame` class.
    """

    def __init__(self, frame_cls, instructions=None):

        # The Frame class the blueprint is for
        self._frame_cls = frame_cls

        # A table of fields names mapped to makers
        self._instructions = instructions or {}

    # Read-only properties

    def frame_cls():
        return self._frame_cls

    # Public methods

    def assemble(self, presets=[]):
        """Assemble a single document using the blueprint and presets"""
        document = {}
        for field_name in self._frame_cls._fields:

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
        for field_name, value in document.items():

            # Use a dedicated instruction if we have one
            if field_name in self._instructions:
                maker = self._instructions[field_name]
                document_copy[field_name] = maker(value)
                continue

            # Check for a preset
            preset = Preset.find(presets, field_name)
            if preset:
                document_copy[field_name] = preset.maker(value)
                continue

        return document_copy