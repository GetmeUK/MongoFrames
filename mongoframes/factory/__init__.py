import copy

__all__ = ['Factory']


class Factory:
    """
    The `Factory` class is responsible for production of fake data for.
    Production of fake data is a two stage process:

    Assembly (see `assemble`)
    :   A `Quota` of documents is assembled based on a `Blueprint`.

        At this stage the documents contain a mixture of static and dynamic
        data. Dynamic data is data that will be transformed during population,
        for example a field might contain a value of `'now,tomorrow'` which on
        population will be converted to a date/time between now and tomorrow.

        Once assembled the generated documents are returned as a list and can be
        either used immediately to populate the database or saved out as a
        template for populating the database in future (for example when
            building a set of test data).

    Population (see `populate`)
    :   A database is populated based on a `Blueprint` and pre-assembled list of
        documents.

        During this stage dynamic data is converted to static data suitable for
        inserting in the database (this process is call finishing).

        Prior to and after inserting the a document into the database the
        `factory_insert` and `factory_inserted` events are triggered to allow
        `Frame` classes to modify the insert behaviour for factories.
    """

    # Public methods

    def assemble(self, blueprint, quota):
        """Assemble a quota of fake documents"""

        # Reset the blueprint
        blueprint.reset()

        # Assemble the documents
        documents = []
        for i in range(0, int(quota)):
            documents.append(blueprint.assemble())

        return documents

    def finish(self, blueprint, documents):
        """Apply finishing to a list of pre-assembled fake documents"""

        # Reset the blueprint
        blueprint.reset()

        # Finish the documents
        finished = []
        for document in documents:
            finished.append(blueprint.finish(document))

        return finished

    def populate(self, blueprint, documents):
        """Populate the database with fake documents"""

        # Finish the documents
        documents = self.finish(blueprint, documents)

        # Convert the documents to frame instances
        frames = []
        for document in documents:
            # Separate out any meta fields
            meta_document = {}
            for field_name in blueprint._meta_fields:
                meta_document[field_name] = document[field_name]
                document.pop(field_name)

            # Initialize the frame
            frame = blueprint.get_frame_cls()(document)

            # Apply any meta fields
            for key, value in meta_document.items():
                setattr(frame, key, value)

            frames.append(frame)

        # Insert the documents
        blueprint.on_fake(frames)
        frames = blueprint.get_frame_cls().insert_many(frames)
        blueprint.on_faked(frames)

        return frames

    def reassemble(self, blueprint, fields, documents):
        """
        Reassemble a the given set of fields for a list of pre-assembed fake
        documents.

        NOTE: Reassembly is done in place, since the data you send the method
        should be JSON type safe if you need to retain a the existing documents
        it is recommended that you copy them using `copy.deepcopy`.
        """

        # Reset the blueprint
        blueprint.reset()

        # Reassemble the documents
        for document in documents:
            blueprint.reassemble(fields, document)