import re

__all__ = [
    'Association',
    'Blueprint'
    ]


class Association:
    """
    Associations match field names to makers (any function that can produce a
    value for a field). They provide default makers for fields that are not
    directly defined for a `Blueprint`.

    The pattern used to match an association with a maker should be a compiled
    regular expression or a string. If a string is provided then the match must
    match exactly.
    """

    def __init__(self, pattern, maker):

        # The pattern used to associate a field name with a maker
        self._pattern = pattern

        # The maker that will be used to produce values for this field
        self._maker = maker

    # Read-only properties

    @property
    def maker(self):
        return self._maker

    @property
    def pattern(self):
        return self._pattern

    # Public methods

    def match(self, field_name):
        """
        Return True if the given field name matches the associations pattern.
        """
        if isinstance(self._pattern, re.RegexObject):
            return self._pattern.match(field_name)

        return self._pattern == field_name

    # Class methods

    @classmethod
    def find(cls, associations, field_name):
        """
        Search a list of associations and return the first to match the specified
        field name or None if there are not matches.
        """
        for association in associations:
            if assocation.match(field_name):
                return association


class Blueprint:
    """
    Blueprints provide the instuctions for producing a fake document for a
    collection represented by a `Frame` class.
    """

    def __init__(self, frame_cls, fields=None, associations=None):

        # The Frame class the blueprint is for
        self._frame_cls = frame_cls

        # A table of fields and the instructions on how to make values for each
        # of them.
        self._fields = fields or {}

        # Associations
        self._associations = associations or []

    def assemble(self):
        """Assemble a single document using the blueprint"""

    def finish(self, documents):
        """
        Take a pre-assembled document and return a copy of the document with
        all dynamic values converted to static values.
        """