from mongoframes import *

__all__ = [
    'InvalidDocument',
    'ValidatedFrame'
    ]


class FormData:
    """
    A class that wraps a dictionary providing a request like object that can be
    used as the `formdata` argument when initializing a `Form`.
    """

    def __init__(self, data):
        self._data = {}
        for key, value in data.items():

            if key not in self._data:
                self._data[key] = []

            if isinstance(value, list):
                self._data[key] += value
            else:
                self._data[key].append(value)

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __contains__(self, name):
        return (name in self._data)

    def get(self, key, default=None):
        if key in self._data:
            return self._data[key][0]
        return default

    def getlist(self, key):
        return self._data.get(key, [])


class InvalidDocument(Exception):
    """
    An exception raised when `save` is called and the document fails validation.
    """

    def __init__(errors):
        super(InvalidDocument, self).__init__()
        self.errors = errors


class ValidatedFrame(Frame):

    # The form attribute should be assigned a WTForm class
    _form = None

    def save(self, *fields):
        """Validate the document before inserting/updating it"""

        # If no form is defined then validation is skipped
        if not self._form:
            return self.upsert(*fields)

        # Build the form data
        if not fields:
            fields = self._fields

        data = {f: self[f] for f in fields}

        # Build the form to validate our data with
        form = self._form(FormData(data))

        # Reduce the form fields to match the data being saved
        for field in form:
            if field.name not in data:
                delattr(form, field.name)

        # Validate the document
        if not form.validate():
            raise InvalidDocument(form.errors)

        # Document is valid, save the changes :)
        self.upsert(*fields)