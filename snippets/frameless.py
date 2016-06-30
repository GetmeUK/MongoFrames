from mongoframes import *
from mongoframes.frames import _FrameMeta

__all__ = [
    'Frameless',
    'SubFrameless'
    ]


class _FramelessMeta(_FrameMeta):
    """
    Meta class for `Frameless` to set the `_collection` value if not set.
    """

    def __new__(meta, name, bases, dct):

        # If no collection name is set then use the class name
        if dct.get('_collection') is None:
            dct['_collection'] = name

        return super(_FramelessMeta, meta).__new__(meta, name, bases, dct)


class Frameless(Frame, metaclass=_FramelessMeta):
    """
    A Frame-like class with no defined set of fields.
    """

    def __getattr__(self, name):
        if '_document' in self.__dict__:
            return self.__dict__['_document'].get(name, None)
        raise AttributeError(
            "'{0}' has no attribute '{1}'".format(self.__class__.__name__, name)
            )

    def __setattr__(self, name, value):
        if '_document' in self.__dict__:
            self.__dict__['_document'][name] = value
        else:
            super(Frameless, self).__setattr__(name, value)

    @property
    def fields(self):
        """Return a list of fields for this document"""
        return self._document.keys()

    @classmethod
    def _flatten_projection(cls, projection):
        """
        Flatten a structured projection (structure projections support for
        projections of (to be) dereferenced fields.
        """

        # If `projection` is empty return a full projection
        if not projection:
            return {'__': False}, {}, {}

        # Flatten the projection
        flat_projection = {}
        references = {}
        subs = {}
        inclusive = True
        for key, value in deepcopy(projection).items():
            if isinstance(value, dict):
                # Store a reference/SubFrame projection
                if '$ref' in value:
                    references[key] = value
                elif '$sub' in value or '$sub.' in value:
                    subs[key] = value
                flat_projection[key] = True

            elif key == '$ref':
                # Strip any `$ref` key
                continue

            elif key == '$sub' or key == '$sub.':
                # Strip any `$sub` key
                continue

            else:
                # Store the root projection value
                flat_projection[key] = value
                inclusive = False

        # If only references and `SubFrames` were specified in the projection
        # then return a full projection.
        if inclusive:
            flat_projection = {'__': False}

        return flat_projection, references, subs


class SubFrameless(SubFrame):
    """
    A SubFrame-like class with no defined set of fields.
    """

    def __getattr__(self, name):
        if '_document' in self.__dict__:
            return self.__dict__['_document'].get(name, None)
        raise AttributeError(
            "'{0}' has no attribute '{1}'".format(self.__class__.__name__, name)
            )

    def __setattr__(self, name, value):
        if '_document' in self.__dict__:
            self.__dict__['_document'][name] = value
        else:
            super(SubFrameless, self).__setattr__(name, value)