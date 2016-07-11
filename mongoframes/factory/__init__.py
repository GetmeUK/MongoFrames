
__all__ = ['Factory']


class Factory:
    """
    The `Factory` class is responsible for production of fake data for.
    """

    def __init__(self):

        # A map of `Frame` classes registered with the factory
        self._frames = {}

    def register(frame_cls):
        """Register a `Frame` class with the factory"""

        assert hasattr(frame_cls, '_factory_blueprint'), \
            frame_cls.__name__ + ' requires a `_factory_blueprint` attribute'

