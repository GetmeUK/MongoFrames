__all__ = ['Preset']


class Preset:
    """
    Presets match field names to makers (any function that can produce a value
    for a field). They provide default makers for fields that are not directly
    defined in a `Blueprints` instructions.

    The pattern used to match a preset with a maker should be a compiled regular
    expression or a string. If a string is provided then the match must match
    exactly.
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
        Return True if the given field name matches the preset's pattern.
        """

        if hasattr(self._pattern, 'match'):
            return self._pattern.match(field_name) is not None

        return self._pattern == field_name

    # Class methods

    @classmethod
    def find(cls, presets, field_name):
        """
        Search a list of presets and return the first to match the specified
        field name or None if there are not matches.
        """
        for preset in presets:
            if preset.match(field_name):
                return preset