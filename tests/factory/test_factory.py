from mongoframes.factory import Factory
from mongoframes.factory import blueprints
from mongoframes.factory import makers
from mongoframes.factory import quotas

from tests.fixtures import *


def test_factory_assemble():
    """
    The `Factory.assemble` method should return a quota of assembled
    documents/dictionaries for the given blueprint.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Configure the factory
    factory = Factory()

    # Assemble a list of documents using the factory
    documents = factory.assemble(DragonBlueprint, quotas.Quota(10))

    # Check the assembled output of the factory is as expected
    for document in documents:
        assert document == {
            'breed': 'Fire-drake',
            'dummy_prop': 'foo',
            'name': 'Burt'
            }

def test_factory_finish():
    """
    The `Factory.assemble` method should return a list of finished
    documents/dictionaries and meta documents/dictionaries in the form
    `[(document, meta_document), ...]` from a blueprint and list of preassembled
    documents/dictionaries.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Configure the factory
    factory = Factory()

    # Assemble a list of documents using the factory
    documents = factory.assemble(DragonBlueprint, quotas.Quota(10))

    # Finish the assembled documents
    documents = factory.finish(DragonBlueprint, documents)

    # Check the assembled output of the factory is as expected
    for document in documents:
        assert document == {
            'breed': 'Fire-drake',
            'name': 'Burt',
            'dummy_prop': 'foo'
            }

def test_factory_populate(mongo_client, mocker):
    """
    The `Factory.populate` method should return populate a database collection
    using using a blueprint and list of preassembled documents/dictionaries.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Configure the factory
    factory = Factory()

    # Assemble a list of documents using the factory
    documents = factory.assemble(DragonBlueprint, quotas.Quota(10))

    # Add listeners for fake and faked
    Dragon._on_fake = lambda sender, frames: print('qwe')
    Dragon._on_faked = lambda sender, frames: None

    mocker.spy(Dragon, '_on_fake')
    mocker.spy(Dragon, '_on_faked')

    Dragon.listen('fake', Dragon._on_fake)
    Dragon.listen('faked', Dragon._on_faked)

    # Populate the database with our fake documents
    frames = factory.populate(DragonBlueprint, documents)

    # Check each maker reset method was called
    assert Dragon._on_fake.call_count == 1
    assert Dragon._on_faked.call_count == 1

    # Check the frames created
    for frame in frames:
        assert frame._id is not None
        assert frame.name == 'Burt'
        assert frame.breed == 'Fire-drake'
        assert frame.dummy_prop


def test_factory_reassemble():
    """
    The `Blueprint.reassemble` method should reassemble the given fields in a
    list of preassembled documents/dictionaries.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Configure the factory
    factory = Factory()

    # Assemble a list of documents using the factory
    documents = factory.assemble(DragonBlueprint, quotas.Quota(10))

    # Re-configure the blueprint and factory
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Fred')
        breed = makers.Static('Cold-drake')
        dummy_prop = makers.Static('bar')

    factory = Factory()

    # Reassemble the documents
    factory.reassemble(DragonBlueprint, {'breed', 'name'}, documents)

    # Check the reassembled output of the factory is as expected
    for document in documents:
        assert document == {
            'breed': 'Cold-drake',
            'dummy_prop': 'foo',
            'name': 'Fred'
            }