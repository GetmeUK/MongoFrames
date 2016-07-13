
__all__ = ['Factory']


class Factory:
    """
    The `Factory` class is responsible for production of fake data for.
    Production of fake data is a two stage process:

    Assembly (see `assemble`)
    :   A `Quota` of documents is assembled based on a set of `Blueprint`s.

        At this stage the documents contain a mixture of static and dynamic
        data. Dynamic data is data that will be transformed during population,
        for example a field might contain a value of `'now,tomorrow'` which on
        population will be converted to a date/time between now and tomorrow.

        Once assembled the generated documents are returned as a dictionary with
        the following structure;

            {
                'blueprint_name': [...documents...],
                ...
            }

        and can be either used immediately to populate the database or saved out
        as a template for populating the database in future (for example when
        building a set of test data).

    Population (see `populate`)
    :   A database is populated based on a set of `Blueprint`s and pre-assembled
        documents.

        During this stage dynamic data is converted to static data suitable for
        inserting in the database.
    """

    def assemble(self, blueprints, quota):
        """Assemble a quota of fake data"""

    def populate(self, blueprints, data):
        """Populate the database with fake data"""