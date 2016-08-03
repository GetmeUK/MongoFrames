import re

from mongoframes.factory import makers
from mongoframes.factory import presets


def test_preset_read_only_props():
    """
    The `Preset` class read-only properties should return the correct values.
    """

    maker = makers.Static('bar')
    preset = presets.Preset('foo', maker)

    # Check the read-only properties of the preset return the correct values
    assert preset.pattern == 'foo'
    assert preset.maker == maker

def test_preset_match():
    """
    The `Preset.match` method should return true if a field name matches a
    pattern.
    """

    # Configure the preset with a simple string match
    preset = presets.Preset('foo', makers.Static('bar'))
    assert preset.match('foo') == True
    assert preset.match('bar') == False

    # Configure the preset with a regular expression match
    preset = presets.Preset(re.compile('foo.*'), makers.Static('bar'))
    assert preset.match('foobar') == True
    assert preset.match('barfoo') == False

def test_preset_find():
    """
    The `Preset.find` class method should return the first preset that matches
    the given field name.
    """
    my_presets = [
        presets.Preset('foo', makers.Static('foo')),
        presets.Preset('bar', makers.Static('bar')),
        presets.Preset('zee', makers.Static('zee')),
        presets.Preset(re.compile('foo.*'), makers.Static('foo*')),
        presets.Preset(re.compile('bar.*'), makers.Static('bar*')),
        presets.Preset(re.compile('zee.*'), makers.Static('zee*'))
        ]

    # Check that `Preset.find` returns the expected presets
    assert presets.Preset.find(my_presets, 'foo') == my_presets[0]
    assert presets.Preset.find(my_presets, 'bar') == my_presets[1]
    assert presets.Preset.find(my_presets, 'zee') == my_presets[2]
    assert presets.Preset.find(my_presets, 'foo1') == my_presets[3]
    assert presets.Preset.find(my_presets, 'bar2') == my_presets[4]
    assert presets.Preset.find(my_presets, 'zee3') == my_presets[5]