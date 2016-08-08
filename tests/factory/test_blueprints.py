import re

from mongoframes.factory import blueprints
from mongoframes.factory import makers
from mongoframes.factory import presets

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
        dummy_prop = makers.Static('foo')

    # Build a list if presets
    my_presets = [presets.Preset('breed', makers.Static('Fire-drake'))]

    # Check the assembled output of the blueprint is as expected
    assembled = DragonBlueprint.assemble(my_presets)

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
        dummy_prop = makers.Static('foo')

    # Build a list if presets
    my_presets = [presets.Preset('breed', makers.Static('Fire-drake'))]

    # Check the finished output of the blueprint is as expected
    finished, meta_finished = DragonBlueprint.finish(
        DragonBlueprint.assemble(my_presets),
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
    class DragonBlueprint(blueprints.Blueprint):

        _frame_cls = Dragon
        _meta_fields = {'dummy_prop'}

        name = makers.Static('Burt')
        dummy_prop = makers.Static('foo')

    # Build a list if presets
    my_presets = [presets.Preset('breed', makers.Static('Fire-drake'))]

    # Spy on the maker reset methods
    mocker.spy(my_presets[0].maker, 'reset')
    mocker.spy(DragonBlueprint._instructions['name'], 'reset')
    mocker.spy(DragonBlueprint._instructions['dummy_prop'], 'reset')

    # Reset the blueprint
    DragonBlueprint.reset(my_presets)

    # Check each maker reset method was called
    assert my_presets[0].maker.reset.call_count == 1
    assert DragonBlueprint._instructions['name'].reset.call_count == 1
    assert DragonBlueprint._instructions['dummy_prop'].reset.call_count == 1