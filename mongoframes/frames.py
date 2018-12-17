from blinker import signal
from bson.objectid import ObjectId
from copy import deepcopy
from datetime import date, datetime, time, timezone

__all__ = [
    'Frame',
    'SubFrame'
    ]


class _BaseFrame:
    """
    Base class for Frames and SubFrames.
    """

    # A cache of key lists generated from path strings used for performance (see
    # `_path_to_keys`.
    _path_to_keys_cache = {}

    def __init__(self, *args, **kwargs):
        # Set the document against the frame (or assign an empty one if one
        # isn't provided).
        if args:
            self._document = args[0]
        else:
            self._document = kwargs

    # Get/Set attribute methods are overwritten to support for setting values
    # against the `_document`. Attribute names are converted to camelcase.

    def __getattr__(self, name):
        if '_document' in self.__dict__ and name in self._fields:
            return self.__dict__['_document'].get(name, None)
        raise AttributeError(
            "'{0}' has no attribute '{1}'".format(self.__class__.__name__, name)
            )

    def __setattr__(self, name, value):
        if '_document' in self.__dict__ and name in self._fields:
            self.__dict__['_document'][name] = value
        else:
            super(_BaseFrame, self).__setattr__(name, value)

    def __getitem__(self, name):
        return self.__dict__['_document'][name]

    def __contains__(self, name):
        return name in self.__dict__['_document']

    def get(self, name, default=None):
        return self.__dict__['_document'].get(name, default)

    # Serializing

    def to_json_type(self):
        """
        Return a dictionary for the document with values converted to JSON safe
        types.
        """
        document_dict = self._json_safe(self._document)
        self._remove_keys(document_dict, self._private_fields)
        return document_dict

    @classmethod
    def _json_safe(cls, value):
        """Return a JSON safe value"""
        # Date
        if type(value) == date:
            return str(value)

        # Datetime
        elif type(value) == datetime:
            return value.strftime('%Y-%m-%d %H:%M:%S')

        # Object Id
        elif isinstance(value, ObjectId):
            return str(value)

        # Frame
        elif isinstance(value, _BaseFrame):
            return value.to_json_type()

        # Lists
        elif isinstance(value, (list, tuple)):
            return [cls._json_safe(v) for v in value]

        # Dictionaries
        elif isinstance(value, dict):
            return {k:cls._json_safe(v) for k, v in value.items()}

        return value

    @classmethod
    def _path_to_keys(cls, path):
        """Return a list of keys for a given path"""

        # Paths are cached for performance
        keys = _BaseFrame._path_to_keys_cache.get(path)
        if keys is None:
            keys = _BaseFrame._path_to_keys_cache[path] = path.split('.')

        return keys

    @classmethod
    def _path_to_value(cls, path, parent_dict):
        """Return a value from a dictionary at the given path"""
        keys = cls._path_to_keys(path)

        # Traverse to the tip of the path
        child_dict = parent_dict
        for key in keys[:-1]:
            child_dict = child_dict.get(key)
            if child_dict is None:
                return

        return child_dict.get(keys[-1])

    @classmethod
    def _remove_keys(cls, parent_dict, paths):
        """
        Remove a list of keys from a dictionary.

        Keys are specified as a series of `.` separated paths for keys in child
        dictionaries, e.g 'parent_key.child_key.grandchild_key'.
        """

        for path in paths:
            keys = cls._path_to_keys(path)

            # Traverse to the tip of the path
            child_dict = parent_dict
            for key in keys[:-1]:
                child_dict = child_dict.get(key)

                if child_dict is None:
                    break

            if child_dict is None:
                continue

            # Remove the key
            if keys[-1] in child_dict:
                child_dict.pop(keys[-1])

    # Public methods

    @classmethod
    def get_fields(cls):
        """Return the set of fields defined for the class"""
        return set(cls._fields)

    @classmethod
    def get_private_fields(cls):
        """Return the set of private fields defined for the class"""
        return set(cls._private_fields)


class _FrameMeta(type):
    """
    Meta class for `Frame`s to ensure an `_id` is present in any defined set of
    fields.
    """

    def __new__(meta, name, bases, dct):

        # If a set of fields is defined ensure it contains `_id`
        if '_fields' in dct and not '_id' in dct['_fields']:
            dct['_fields'].update({'_id'})

        # If no collection name is set then use the class name
        if dct.get('_collection') is None:
            dct['_collection'] = name

        return super(_FrameMeta, meta).__new__(meta, name, bases, dct)


class Frame(_BaseFrame, metaclass=_FrameMeta):
    """
    Frames allow documents to be wrapped in a class adding support for dot
    notation access to attributes and numerous short-cut/helper methods.
    """

    # The MongoDB client used to interface with the database
    _client = None

    # The database on which this collection the class represents is located
    _db = None

    # The database collection this class represents
    _collection = None

    # The documents defined fields
    _fields = set()

    # A set of private fields that will be excluded from the output of
    # `to_json_type`.
    _private_fields = set()

    # Default projection
    _default_projection = None

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._id == other._id

    def __hash__(self):
        if not self._id:
            raise TypeError('Cannot hash a document without an `_id` set.')
        return int(str(self._id), 16)

    def __lt__(self, other):
        return self._id < other._id

    # Operations

    def insert(self):
        """Insert this document"""
        from mongoframes.queries import to_refs

        # Send insert signal
        signal('insert').send(self.__class__, frames=[self])

        # Prepare the document to be inserted
        document = to_refs(self._document)

        # Insert the document and update the Id
        self._id = self.get_collection().insert_one(document).inserted_id

        # Send inserted signal
        signal('inserted').send(self.__class__, frames=[self])

    def update(self, *fields):
        """
        Update this document. Optionally a specific list of fields to update can
        be specified.
        """
        from mongoframes.queries import to_refs

        assert '_id' in self._document, "Can't update documents without `_id`"

        # Send update signal
        signal('update').send(self.__class__, frames=[self])

        # Check for selective updates
        if len(fields) > 0:
            document = {}
            for field in fields:
                document[field] = self._path_to_value(field, self._document)
        else:
            document = self._document

        # Prepare the document to be updated
        document = to_refs(document)
        document.pop('_id', None)

        # Update the document
        self.get_collection().update_one({'_id': self._id}, {'$set': document})

        # Send updated signal
        signal('updated').send(self.__class__, frames=[self])

    def upsert(self, *fields):
        """
        Update or Insert this document depending on whether it exists or not.
        The presense of an `_id` value in the document is used to determine if
        the document exists.

        NOTE: This method is not the same as specifying the `upsert` flag when
        calling MongoDB. When called for a document with an `_id` value, this
        method will call the database to see if a record with that Id exists,
        if not it will call `insert`, if so it will call `update`. This
        operation is therefore not atomic and much slower than the equivalent
        MongoDB operation (due to the extra call).
        """

        # If no `_id` is provided then we insert the document
        if not self._id:
            return self.insert()

        # If an `_id` is provided then we need to check if it exists before
        # performing the `upsert`.
        #
        if self.count({'_id': self._id}) == 0:
            self.insert()
        else:
            self.update(*fields)

    def delete(self):
        """Delete this document"""

        assert '_id' in self._document, "Can't delete documents without `_id`"

        # Send delete signal
        signal('delete').send(self.__class__, frames=[self])

        # Delete the document
        self.get_collection().delete_one({'_id': self._id})

        # Send deleted signal
        signal('deleted').send(self.__class__, frames=[self])

    @classmethod
    def insert_many(cls, documents):
        """Insert a list of documents"""
        from mongoframes.queries import to_refs

        # Ensure all documents have been converted to frames
        frames = cls._ensure_frames(documents)

        # Send insert signal
        signal('insert').send(cls, frames=frames)

        # Prepare the documents to be inserted
        documents = [to_refs(f._document) for f in frames]

        # Bulk insert
        ids = cls.get_collection().insert_many(documents).inserted_ids

        # Apply the Ids to the frames
        for i, id in enumerate(ids):
            frames[i]._id = id

        # Send inserted signal
        signal('inserted').send(cls, frames=frames)

        return frames

    @classmethod
    def update_many(cls, documents, *fields):
        """
        Update multiple documents. Optionally a specific list of fields to
        update can be specified.
        """
        from mongoframes.queries import to_refs

        # Ensure all documents have been converted to frames
        frames = cls._ensure_frames(documents)

        all_count = len(documents)
        assert len([f for f in frames if '_id' in f._document]) == all_count, \
                "Can't update documents without `_id`s"

        # Send update signal
        signal('update').send(cls, frames=frames)

        # Prepare the documents to be updated

        # Check for selective updates
        if len(fields) > 0:
            documents = []
            for frame in frames:
                document = {'_id': frame._id}
                for field in fields:
                    document[field] = cls._path_to_value(
                        field,
                        frame._document
                        )
                documents.append(to_refs(document))
        else:
            documents = [to_refs(f._document) for f in frames]

        # Update the documents
        for document in documents:
            _id = document.pop('_id')
            cls.get_collection().update(
                {'_id': _id}, {'$set': document})

        # Send updated signal
        signal('updated').send(cls, frames=frames)

    @classmethod
    def delete_many(cls, documents):
        """Delete multiple documents"""

        # Ensure all documents have been converted to frames
        frames = cls._ensure_frames(documents)

        all_count = len(documents)
        assert len([f for f in frames if '_id' in f._document]) == all_count, \
                "Can't delete documents without `_id`s"

        # Send delete signal
        signal('delete').send(cls, frames=frames)

        # Prepare the documents to be deleted
        ids = [f._id for f in frames]

        # Delete the documents
        cls.get_collection().delete_many({'_id': {'$in': ids}})

        # Send deleted signal
        signal('deleted').send(cls, frames=frames)

    @classmethod
    def _ensure_frames(cls, documents):
        """
        Ensure all items in a list are frames by converting those that aren't.
        """
        frames = []
        for document in documents:
            if not isinstance(document, Frame):
                frames.append(cls(document))
            else:
                frames.append(document)
        return frames

    # Querying

    def reload(self, **kwargs):
        """Reload the document"""
        frame = self.one({'_id': self._id}, **kwargs)
        self._document = frame._document

    @classmethod
    def by_id(cls, id, **kwargs):
        """Get a document by ID"""
        return cls.one({'_id': id}, **kwargs)

    @classmethod
    def count(cls, filter=None, **kwargs):
        """Return a count of documents matching the filter"""
        from mongoframes.queries import Condition, Group, to_refs

        if isinstance(filter, (Condition, Group)):
            filter = filter.to_dict()

        return cls.get_collection().count(to_refs(filter), **kwargs)

    @classmethod
    def ids(cls, filter=None, **kwargs):
        """Return a list of Ids for documents matching the filter"""
        from mongoframes.queries import Condition, Group, to_refs

        # Find the documents
        if isinstance(filter, (Condition, Group)):
            filter = filter.to_dict()

        documents = cls.get_collection().find(
            to_refs(filter),
            projection={'_id': True},
            **kwargs
            )

        return [d['_id'] for d in list(documents)]

    @classmethod
    def one(cls, filter=None, **kwargs):
        """Return the first document matching the filter"""
        from mongoframes.queries import Condition, Group, to_refs

        # Flatten the projection
        kwargs['projection'], references, subs = \
                cls._flatten_projection(
                    kwargs.get('projection', cls._default_projection)
                    )

        # Find the document
        if isinstance(filter, (Condition, Group)):
            filter = filter.to_dict()

        document = cls.get_collection().find_one(to_refs(filter), **kwargs)

        # Make sure we found a document
        if not document:
            return

        # Dereference the document (if required)
        if references:
            cls._dereference([document], references)

        # Add sub-frames to the document (if required)
        if subs:
            cls._apply_sub_frames([document], subs)

        return cls(document)

    @classmethod
    def many(cls, filter=None, **kwargs):
        """Return a list of documents matching the filter"""
        from mongoframes.queries import Condition, Group, to_refs

        # Flatten the projection
        kwargs['projection'], references, subs = \
                cls._flatten_projection(
                    kwargs.get('projection', cls._default_projection)
                    )

        # Find the documents
        if isinstance(filter, (Condition, Group)):
            filter = filter.to_dict()

        documents = list(cls.get_collection().find(to_refs(filter), **kwargs))

        # Dereference the documents (if required)
        if references:
            cls._dereference(documents, references)

        # Add sub-frames to the documents (if required)
        if subs:
            cls._apply_sub_frames(documents, subs)

        return [cls(d) for d in documents]

    @classmethod
    def _apply_sub_frames(cls, documents, subs):
        """Convert embedded documents to sub-frames for one or more documents"""

        # Dereference each reference
        for path, projection in subs.items():

            # Get the SubFrame class we'll use to wrap the embedded document
            sub = None
            expect_map = False
            if '$sub' in projection:
                sub = projection.pop('$sub')
            elif '$sub.' in projection:
                sub = projection.pop('$sub.')
                expect_map = True
            else:
                continue

            # Add sub-frames to the documents
            raw_subs = []
            for document in documents:
                value = cls._path_to_value(path, document)
                if value is None:
                    continue

                if isinstance(value, dict):
                    if expect_map:
                        # Dictionary of embedded documents
                        raw_subs += value.values()
                        for k, v in value.items():
                            if isinstance(v ,list):
                                value[k] = [
                                    sub(u) for u in v if isinstance(u, dict)]
                            else:
                                value[k] = sub(v)

                    # Single embedded document
                    else:
                        raw_subs.append(value)
                        value = sub(value)

                elif isinstance(value, list):
                    # List of embedded documents
                    raw_subs += value
                    value = [sub(v) for v in value if isinstance(v, dict)]

                else:
                    raise TypeError('Not a supported sub-frame type')

                child_document = document
                keys = cls._path_to_keys(path)
                for key in keys[:-1]:
                    child_document = child_document[key]
                child_document[keys[-1]] = value

            # Apply the projection to the list of sub frames
            if projection:
                sub._apply_projection(raw_subs, projection)

    @classmethod
    def _dereference(cls, documents, references):
        """Dereference one or more documents"""

        # Dereference each reference
        for path, projection in references.items():

            # Check there is a $ref in the projection, else skip it
            if '$ref' not in projection:
                continue

            # Collect Ids of documents to dereference
            ids = set()
            for document in documents:
                value = cls._path_to_value(path, document)
                if not value:
                    continue

                if isinstance(value, list):
                    ids.update(value)

                elif isinstance(value, dict):
                    ids.update(value.values())

                else:
                    ids.add(value)

            # Find the referenced documents
            ref = projection.pop('$ref')
            frames = ref.many(
                {'_id': {'$in': list(ids)}},
                projection=projection
                )
            frames = {f._id: f for f in frames}

            # Add dereferenced frames to the document
            for document in documents:
                value = cls._path_to_value(path, document)
                if not value:
                    continue

                if isinstance(value, list):
                    # List of references
                    value = [frames[id] for id in value if id in frames]

                elif isinstance(value, dict):
                    # Dictionary of references
                    value = {key: frames.get(id) for key, id in value.items()}

                else:
                    value = frames.get(value, None)

                child_document = document
                keys = cls._path_to_keys(path)
                for key in keys[:-1]:
                    child_document = child_document[key]
                child_document[keys[-1]] = value

    @classmethod
    def _flatten_projection(cls, projection):
        """
        Flatten a structured projection (structure projections support for
        projections of (to be) dereferenced fields.
        """

        # If `projection` is empty return a full projection based on `_fields`
        if not projection:
            return {f: True for f in cls._fields}, {}, {}

        # Flatten the projection
        flat_projection = {}
        references = {}
        subs = {}
        inclusive = True
        for key, value in deepcopy(projection).items():
            if isinstance(value, dict):

                # Build the projection value for the field (allowing for
                # special mongo directives).
                project_value = {
                    k: v for k, v in value.items()
                    if k.startswith('$') and k not in ['$ref', '$sub', '$sub.']
                }
                if len(project_value) == 0:
                    project_value = True
                else:
                    inclusive = False

                # Store a reference/sub-frame projection
                if '$ref' in value:
                    references[key] = value

                elif '$sub' in value or '$sub.' in value:
                    subs[key] = value

                flat_projection[key] = project_value

            elif key == '$ref':
                # Strip any $ref key
                continue

            elif key == '$sub' or key == '$sub.':
                # Strip any $sub key
                continue

            else:
                # Store the root projection value
                flat_projection[key] = value
                inclusive = False

        # If only references and sub-frames where specified in the projection
        # then return a full projection based on `_fields`.
        if inclusive:
            flat_projection = {f: True for f in cls._fields}

        return flat_projection, references, subs

    # Integrity helpers

    @staticmethod
    def timestamp_insert(sender, frames):
        """
        Timestamp the created and modified fields for all documents. This method
        should be bound to a frame class like so:

        ```
        MyFrameClass.listen('insert', MyFrameClass.timestamp_insert)
        ```
        """
        for frame in frames:
            timestamp = datetime.now(timezone.utc)
            frame.created = timestamp
            frame.modified = timestamp

    @staticmethod
    def timestamp_update(sender, frames):
        """
        Timestamp the modified field for all documents. This method should be
        bound to a frame class like so:

        ```
        MyFrameClass.listen('update', MyFrameClass.timestamp_update)
        ```
        """
        for frame in frames:
            frame.modified = datetime.now(timezone.utc)

    @classmethod
    def cascade(cls, ref_cls, field, frames):
        """Apply a cascading delete (does not emit signals)"""
        from mongoframes.queries import to_refs
        ids = [to_refs(f[field]) for f in frames if f.get(field)]
        ref_cls.get_collection().delete_many({'_id': {'$in': ids}})

    @classmethod
    def nullify(cls, ref_cls, field, frames):
        """Nullify a reference field (does not emit signals)"""
        from mongoframes.queries import to_refs
        ids = [to_refs(f) for f in frames]
        ref_cls.get_collection().update_many(
            {field: {'$in': ids}},
            {'$set': {field: None}}
            )

    @classmethod
    def pull(cls, ref_cls, field, frames):
        """Pull references from a list field (does not emit signals)"""
        from mongoframes.queries import to_refs
        ids = [to_refs(f) for f in frames]
        ref_cls.get_collection().update_many(
            {field: {'$in': ids}},
            {'$pull': {field: {'$in': ids}}}
            )

    # Signals

    @classmethod
    def listen(cls, event, func):
        """Add a callback for a signal against the class"""
        signal(event).connect(func, sender=cls)

    @classmethod
    def stop_listening(cls, event, func):
        """Remove a callback for a signal against the class"""
        signal(event).disconnect(func, sender=cls)

    # Misc.

    @classmethod
    def get_collection(cls):
        """Return a reference to the database collection for the class"""
        return getattr(cls.get_db(), cls._collection)

    @classmethod
    def get_db(cls):
        """Return the database for the collection"""
        if cls._db:
            return getattr(cls._client, cls._db)
        return cls._client.get_default_database()


class SubFrame(_BaseFrame):
    """
    Sub-frames allow embedded documents to be wrapped in a class adding support
    for dot notation access to attributes.
    """

    # The documents defined fields
    _fields = set()

    # A set of private fields that will be excluded from the output of
    # `to_json_type`.
    _private_fields = set()

    @classmethod
    def _apply_projection(cls, documents, projection):

        # Find reference and sub-frame mappings
        references = {}
        subs = {}
        for key, value in deepcopy(projection).items():

            if not isinstance(value, dict):
                continue

            # Store a reference/sub-frame projection
            if '$ref' in value:
                references[key] = value
            elif '$sub' in value or '$sub.' in value:
                subs[key] = value

        # Dereference the documents (if required)
        if references:
            Frame._dereference(documents, references)

        # Add sub-frames to the documents (if required)
        if subs:
            Frame._apply_sub_frames(documents, subs)
