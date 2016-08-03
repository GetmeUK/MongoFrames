import re

from mongoframes.factory import blueprints
from mongoframes.factory import makers
from mongoframes.factory import presets

from tests.fixtures import *


def test_blueprint_read_only_props():
    """
    The `Blueprint` class read-only properties should return the correct values.
    """

    blueprint = blueprints.Blueprint(Dragon)

    # Check the read-only properties of the preset return the correct values
    assert blueprint.frame_cls == Dragon

def test_blueprint_assemble():
    """
    The `Blueprint.assemble` method should return an assembled a
    document/dictionary for the blueprint.
    """

    # Configure the blueprint
    my_presets = [presets.Preset('breed', makers.Static('Fire-drake'))]
    instructions = {
        'name': makers.Static('Burt'),
        'dummy_prop': makers.Static('foo')
        }
    meta_fields = {'dummy_prop'}
    blueprint = blueprints.Blueprint(Dragon, instructions, meta_fields)

    # Check the assembled output of the blueprint is as expected
    assembled = blueprint.assemble(my_presets)

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
    my_presets = [presets.Preset('breed', makers.Static('Fire-drake'))]
    instructions = {
        'name': makers.Static('Burt'),
        'dummy_prop': makers.Static('foo')
        }
    meta_fields = {'dummy_prop'}
    blueprint = blueprints.Blueprint(Dragon, instructions, meta_fields)

    # Check the finished output of the blueprint is as expected
    finished, meta_finished = blueprint.finish(
        blueprint.assemble(my_presets),
        my_presets
        )

    assert finished == {'breed': 'Fire-drake', 'name': 'Burt'}
    assert meta_finished == {'dummy_prop': 'foo'}

def test_blueprint_reset(mocker):
    """
    The `Blueprint.reset` method should call the reset of all makers in the
    blueprints instructions and any in the given list of presets.
    """

    # Configure the blueprint
    my_presets = [presets.Preset('breed', makers.Static('Fire-drake'))]
    instructions = {
        'name': makers.Static('Burt'),
        'dummy_prop': makers.Static('foo')
        }
    meta_fields = {'dummy_prop'}
    blueprint = blueprints.Blueprint(Dragon, instructions, meta_fields)

    # Spy on the maker reset methods
    mocker.spy(my_presets[0].maker, 'reset')
    mocker.spy(instructions['name'], 'reset')
    mocker.spy(instructions['dummy_prop'], 'reset')

    # Reset the blueprint
    blueprint.reset(my_presets)

    # Check each maker reset method was called
    assert my_presets[0].maker.reset.call_count == 1
    assert instructions['name'].reset.call_count == 1
    assert instructions['dummy_prop'].reset.call_count == 1