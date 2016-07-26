from mongoframes.factory import makers

# TODO
# @@ DictOf
# @@ Faker
# @@ ListOf
# @@ Reference
# @@ SubFactory
# @@ Unique


def test_lambda():
    """
    Lambda makers should return the output of the function you initialize them
    with.
    """

    # Configured as assembled
    maker = makers.Lambda(lambda: 'foo')

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == 'foo'

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 'foo'

    # Configured as finisher
    maker = makers.Lambda(lambda v: 'bar', assembler=False, finisher=True)

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == None

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 'bar'

    # Configured as both an assembler and finisher
    def func(value=None):
        if value:
            return value + 'bar'
        return 'foo'

    maker = makers.Lambda(func, finisher=True)

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == 'foo'

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == 'foobar'


def test_static():
    """Static makers should return the value you initialize them with"""

    # Configured as assembler
    value = {'foo': 'bar'}
    maker = makers.Static(value)

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == value

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == value

    # Configured as finisher
    value = {'foo': 'bar'}
    maker = makers.Static(value, assembler=False)

    # Check the assembled result
    assembled = maker._assemble()
    assert assembled == None

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == value