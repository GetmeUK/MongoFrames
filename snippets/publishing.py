from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

from flask import g
from mongoframes import *
import pymongo

__all__ = ['PublisherFrame']


class PublisherFrame(Frame):
    """
    The PublisherFrame class supports documents that implement the draft >
    published workflow.
    """

    _fields = {'_uid', 'revision'}
    _unpublished_fields = {'_id'}

    def __init__(self, *args, **kwargs):
        super(PublisherFrame, self).__init__(*args, **kwargs)

        # Ensure a UID is assigned to the document
        if not self._uid:
            self._uid = str(uuid4())

    @property
    def can_publish(self):
        """
        Return True if there is a draft version of the document that's ready to
        be published.
        """
        with self.published_context():
            published = self.one(
                Q._uid == self._uid,
                projection={'revision': True}
                )

        if not published:
            return True

        with self.draft_context():
            draft = self.one(Q._uid == self._uid, projection={'revision': True})

        return draft.revision > published.revision

    @property
    def can_revert(self):
        """
        Return True if we can revert the draft version of the document to the
        currently published version.
        """

        if self.can_publish:
            with self.published_context():
                return self.count(Q._uid == self._uid) > 0

        return False

    def get_publisher_doc(self):
        """Return a publish safe version of the frame's document"""
        with self.draft_context():
            # Select the draft document from the database
            draft = self.one(Q._uid == self._uid)
            publisher_doc = draft._document

            # Remove any keys from the document that should not be transferred
            # when publishing.
            self._remove_keys(publisher_doc, self._unpublished_fields)

        return publisher_doc

    def publish(self):
        """
        Publish the current document.

        NOTE: You must have saved any changes to the draft version of the
        document before publishing, unsaved changes wont be published.
        """
        publisher_doc = self.get_publisher_doc()

        with self.published_context():
            # Select the published document
            published = self.one(Q._uid == self._uid)

            # If there's no published version of the document create one
            if not published:
                published = self.__class__()

            # Update the document
            for field, value in publisher_doc.items():
                setattr(published, field, value)

            # Save published version
            published.upsert()

        # Set the revisions number for draft/published version, we use PyMongo
        # directly as it's more convienent to use the shared `_uid`.
        now = datetime.now()

        with self.draft_context():
            self.get_collection().update(
                {'_uid': self._uid},
                {'$set': {'revision': now}}
                )

        with self.published_context():
            self.get_collection().update(
                {'_uid': self._uid},
                {'$set': {'revision': now}}
                )

    def new_revision(self, *fields):
        """Save a new revision of the document"""

        # Ensure this document is a draft
        if not self._id:
            assert g.get('draft'), \
                    'Only draft documents can be assigned new revisions'
        else:
            with self.draft_context():
                assert self.count(Q._id == self._id) == 1, \
                        'Only draft documents can be assigned new revisions'

        # Set the revision
        if len(fields) > 0:
           fields.append('revision')

        self.revision = datetime.now()

        # Update the document
        self.upsert(*fields)

    def delete(self):
        """Delete this document and any counterpart document"""

        with self.draft_context():
            draft = self.one(Q._uid == self._uid)
            if draft:
                super(PublisherFrame, draft).delete()

        with self.published_context():
            published = self.one(Q._uid == self._uid)
            if published:
                super(PublisherFrame, published).delete()

    def revert(self):
        """Revert the document to currently published version"""

        with self.draft_context():
            draft = self.one(Q._uid == self._uid)

        with self.published_context():
            published = self.one(Q._uid == self._uid)

        for field, value in draft._document.items():
            if field in self._unpublished_fields:
                continue
            setattr(draft, field, getattr(published, field))

        # Revert the revision
        draft.revision = published.revision

        draft.update()

    @classmethod
    def get_collection(cls):
        """Return a reference to the database collection for the class"""

        # By default the collection returned will be the published collection,
        # however if the `draft` flag has been set against the global context
        # (e.g `g`) then the collection returned will contain draft documents.

        if g.get('draft'):
            return getattr(
                cls.get_db(),
                '{collection}_draft'.format(collection=cls._collection)
                )

        return getattr(cls.get_db(), cls._collection)

    # Contexts

    @classmethod
    @contextmanager
    def draft_context(cls):
        """Set the context to draft"""
        previous_state = g.get('draft')
        try:
            g.draft = True
            yield
        finally:
            g.draft = previous_state

    @classmethod
    @contextmanager
    def published_context(cls):
        """Set the context to published"""
        previous_state = g.get('draft')
        try:
            g.draft = False
            yield
        finally:
            g.draft = previous_state