from collections import OrderedDict
import re

from mongoframes.factory import blueprints
from mongoframes.factory import makers

from tests.fixtures import *


def test_blueprint_defaults():
    """
    Defining a `Blueprint` class should provide some defaults.
    """

    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon

    assert DragonBlueprint._frame_cls == Dragon
    assert DragonBlueprint._instructions == {}
    assert DragonBlueprint._meta_fields == set([])

def test_blueprint_getters():
    """
    The `Blueprint` getter methods:

    - `get_frame_cls`
    - `get_instructions`
    - `get_meta_fields`

    Should return correct values.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Check the getter return values
    assert DragonBlueprint.get_frame_cls() == Dragon
    assert DragonBlueprint.get_instructions() == OrderedDict([
        ('name', DragonBlueprint.name),
        ('breed', DragonBlueprint.breed),
        ('dummy_prop', DragonBlueprint.dummy_prop)
        ])
    assert DragonBlueprint.get_meta_fields() == {'dummy_prop'}

def test_blueprint_assemble():
    """
    The `Blueprint.assemble` method should return an assembled a
    document/dictionary for the blueprint.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Check the assembled output of the blueprint is as expected
    assembled = DragonBlueprint.assemble()

    assert assembled == {
        'breed': 'Fire-drake',
        'dummy_prop': 'foo',
        'name': 'Burt'
        }

def test_blueprint_finish():
    """
    The `Blueprint.finish` method should return a finished document/dictionary
    and meta document/dictionary for the blueprint.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Check the finished output of the blueprint is as expected
    finished = DragonBlueprint.finish(DragonBlueprint.assemble())

    assert finished == {
        'breed': 'Fire-drake',
        'dummy_prop': 'foo',
        'name': 'Burt'
        }

def test_blueprint_reassemble():
    """
    The `Blueprint.reassemble` method should reassemble the given fields in a
    preassembled document/dictionary for the blueprint.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Check the assembled output of the blueprint is as expected
    assembled = DragonBlueprint.assemble()

    # Re-configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Fred')
        breed = makers.Static('Cold-drake')
        dummy_prop = makers.Static('bar')

    # Check the reassembled output for the blueprint is as expected
    DragonBlueprint.reassemble({'breed', 'name'}, assembled)

    assert assembled == {
        'breed': 'Cold-drake',
        'dummy_prop': 'foo',
        'name': 'Fred'
        }

def test_blueprint_reset(mocker):
    """
    The `Blueprint.reset` method should call the reset of all makers in the
    blueprints instructions.
    """

    # Configure the blueprint
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        breed = makers.Static('Fire-drake')
        dummy_prop = makers.Static('foo')

    # Spy on the maker reset methods
    mocker.spy(DragonBlueprint._instructions['name'], 'reset')
    mocker.spy(DragonBlueprint._instructions['breed'], 'reset')
    mocker.spy(DragonBlueprint._instructions['dummy_prop'], 'reset')

    # Reset the blueprint
    DragonBlueprint.reset()

    # Check each maker reset method was called
    assert DragonBlueprint._instructions['name'].reset.call_count == 1
    assert DragonBlueprint._instructions['breed'].reset.call_count == 1
    assert DragonBlueprint._instructions['dummy_prop'].reset.call_count == 1