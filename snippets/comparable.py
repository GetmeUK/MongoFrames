from mongoframes import *
from datetime import date

__all__ = [
    'ChangeLogEntry',
    'ComparableFrame'
    ]


class ChangeLogEntry(Frame):
    """
    A class for implementing a change log. Each tracked change to a document is
    logged in the `ChangeLogEntry` collection.
    """

    _fields = {
        'created',
        'documents',
        'documents_sticky_label',
        'user',
        'user_sticky_label',
        'type',
        'details'
        }

    # A set of HTML templates used to output the *diff* for a change log entry
    _templates = {
        'add': '''
            <div class="change change--add">
                <div class="change__field">{field}</div>
                <div class="change__values">
                    <div class="change__value change__value--new">
                        {new_value}
                    </div>
                </div>
            </div>
            ''',

        'update': '''
            <div class="change change--update">
                <div class="change__field">{field}</div>
                <div class="change__values">
                    <div class="change__value change__value--original">
                        {original_value}
                    </div>
                    <div class="change__value change__value--new">
                        {new_value}
                    </div>
                </div>
            </div>
            ''',

        'delete': '''
            <div class="change change--delete">
                <div class="change__field">{field}</div>
                <div class="change__values">
                    <div class="change__value change__value--original">
                        {original_value}
                    </div>
                </div>
            </div>
            '''
        }

    @property
    def is_diff(self):
        """Return true if there are any differences logged"""
        if not isinstance(self.details, dict):
            return False

        for key in ['additions', 'updates', 'deletions']:
            if self.details.get(key, None):
                return True

        return False

    def add_diff(self, original, new):
        """
        Set the details of the change log entry as the difference between two
        dictionaries (original vs. new). The change log uses the following
        format:

        {
            'additions': {
                'field_name': 'value',
                ...
            },
            'updates': {
               'field_name': ['original_value', 'new_value'],
                ...
            },
            'deletions': {
                'field_name': ['original_value']
            }
        }

        Values are tested for equality, there is special case handling for
        `Frame` class instances (see `diff_safe`) and fields with the word
        password in their name are redacted.

        Note: Where possible use diff structures that are flat, performing a
        diff on a dictionary which contains sub-dictionaries is not recommended
        as the verbose output (see `diff_to_html`) is optimized for flat
        structures.
        """
        changes = {}

        # Check for additions and updates
        for new_key, new_value in new.items():

            # Additions
            if new_key not in original:
                if 'additions' not in changes:
                    changes['additions'] = {}
                new_value = self.diff_safe(new_value)
                changes['additions'][new_key] = new_value

            # Updates
            elif original[new_key] != new_value:
                if 'updates' not in changes:
                    changes['updates'] = {}

                original_value = self.diff_safe(original[new_key])
                new_value = self.diff_safe(new_value)

                changes['updates'][new_key] = [original_value, new_value]

                # Check for password type fields and redact them
                if 'password' in new_key:
                    changes['updates'][new_key] = ['*****', '*****']

        # Check for deletions
        for original_key, original_value in original.items():
            if original_key not in new:
                if 'deletions' not in changes:
                    changes['deletions'] = {}

                original_value = self.diff_safe(original_value)
                changes['deletions'][original_key] = original_value

        self.details = changes

    @classmethod
    def diff_to_html(cls, details):
        """Return an entry's details in HTML format"""
        changes = []

        # Check that there are details to convert to HMTL
        if not details:
            return ''

        def _frame(value):
            """
            Handle converted `Frame` references where the human identifier is
            stored against the `_str` key.
            """
            if isinstance(value, dict) and '_str' in value:
                return value['_str']
            elif isinstance(value, list):
                return ', '.join([_frame(v) for v in value])
            return str(value)

        # Additions
        fields = sorted(details.get('additions', {}))
        for field in fields:
            new_value = _frame(details['additions'][field])
            if isinstance(new_value, list):
                new_value = ', '.join([_frame(v) for v in new_value])

            change = cls._templates['add'].format(
                field=field,
                new_value=new_value
                )
            changes.append(change)

        # Updates
        fields = sorted(details.get('updates', {}))
        for field in fields:
            original_value = _(details['updates'][field][0])
            if isinstance(original_value, list):
                original_value = ', '.join([_frame(v) for v in original_value])

            new_value = _frame(details['updates'][field][1])
            if isinstance(new_value, list):
                new_value = ', '.join([_frame(v) for v in new_value])

            change = cls._templates['update'].format(
                field=field,
                original_value=original_value,
                new_value=new_value
                )
            changes.append(change)

        # Deletions
        fields = sorted(details.get('deletions', {}))
        for field in fields:
            original_value = _frame(details['deletions'][field])
            if isinstance(original_value, list):
                original_value = ', '.join([_frame(v) for v in original_value])

            change = cls._templates['delete'].format(
                field=field,
                original_value=original_value
                )
            changes.append(change)

        return '\n'.join(changes)

    @classmethod
    def diff_safe(cls, value):
        """Return a value that can be safely stored as a diff"""
        if isinstance(value, Frame):
            return {'_str': str(value), '_id': value._id}
        elif isinstance(value, (list, tuple)):
            return [cls.diff_safe(v) for v in value]
        return value

    @staticmethod
    def _on_insert(sender, frames=[]):
        for frame in frames:

            # Record *sticky* labels for the change so even if the documents or
            # user are removed from the system their details are retained.
            pairs = [(d, d.__class__.__name__) for d in frame.documents]
            frame.documents_sticky_label = ', '.join(
                ['{0} ({1})'.format(*p) for p in pairs]
                )

            if frame.user:
                frame.user_sticky_label = str(frame.user)

ChangeLogEntry.listen('insert', ChangeLogEntry.timestamp_insert)
ChangeLogEntry.listen('insert', ChangeLogEntry._on_insert)


class ComparableFrame(Frame):
    """
    A Frame-like base class that provides support for tracking changes to
    documents.

    Some important rules for creating comparable frames:

    - Override the `__str__` method of the class to return a human friendly
      identity as this method is called when generating a sticky label for the
      class.
    - Define which fields are references and which `Frame` class they reference
      in the `_compared_refs` dictionary if you don't you'll only be able to see
      that the ID has changed there will be nothing human identifiable.
    """

    # A set of fields that should be exluded from comparisons/tracking
    _uncompared_fields = {'_id'}

    # A map of reference fields and the frames they reference
    _compared_refs = {}

    @property
    def comparable(self):
        """Return a dictionary that can be compared"""
        document_dict = self.compare_safe(self._document)

        # Remove uncompared fields
        self._remove_keys(document_dict, self._uncompared_fields)

        # Remove any empty values
        clean_document_dict = {}
        for k, v in document_dict.items():
            if not v and not isinstance(v, (int, float)):
                continue
            clean_document_dict[k] = v

        # Convert any referenced fields to Frames
        for ref_field, ref_cls in self._compared_refs.items():
            ref = getattr(self, ref_field)
            if not ref:
                continue

            # Check for fields which contain a list of references
            if isinstance(ref, list):
                if isinstance(ref[0], Frame):
                    continue

                # Dereference the list of reference IDs
                setattr(
                    clean_document_dict,
                    ref_field,
                    ref_cls.many(In(Q._id, ref))
                    )

            else:
                if isinstance(ref, Frame):
                    continue

                # Dereference the reference ID
                setattr(
                    clean_document_dict,
                    ref_field,
                    ref_cls.byId(ref)
                    )

        return clean_document_dict

    def logged_delete(self, user):
        """Delete the document and log the event in the change log"""

        self.delete()

        # Log the change
        entry = ChangeLogEntry({
            'type': 'DELETED',
            'documents': [self],
            'user': user
            })
        entry.insert()

        return entry

    def logged_insert(self, user, form):
        """Create and insert the document and log the event in the change log"""

        data = form.populate_obj(self)

        # Insert the frame's document
        self.insert()

        # Log the insert
        entry = ChangeLogEntry({
            'type': 'ADDED',
            'documents': [self],
            'user': user
            })
        entry.insert()

        return entry

    def logged_update(self, user, data, *fields):
        """
        Update the document with the dictionary of data provided and log the
        event in the change log.
        """

        # Get a copy of the frames comparable data before the update
        original = self.comparable

        # Update the frame
        _fields = fields
        if len(fields) == 0:
             _fields = data.keys()

        for field in _fields:
            setattr(self, k, v)

        self.update(*fields)

        # Create an entry and perform a diff
        entry = ChangeLogEntry({
            'type': 'UPDATED',
            'documents': [self],
            'user': user
            })
        entry.add_diff(original, self.comparable)

        # Check there's a change to apply/log
        if not entry.is_diff:
            return
        entry.insert()

        return entry

    @classmethod
    def compare_safe(cls, value):
        """Return a value that can be safely compared"""

        # Date
        if type(value) == date:
            return str(value)

        # Lists
        elif isinstance(value, (list, tuple)):
            return [cls.compare_safe(v) for v in value]

        # Dictionaries
        elif isinstance(value, dict):
            return {k: cls.compare_safe(v) for k, v in value.items()}

        return value