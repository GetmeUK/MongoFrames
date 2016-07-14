
__all__ = ['Quota']


class Quantity:
    """
    A base class for classes looking to add variation to `Quota` quantities. The
    base class behaves the same as passing a number to a `Quota`.
    """

    def __init__(self, quantity):
        self._quantity = 0

    def __call__(self):
        return self._quantity


class Quota:
    """
    Quota's provide instructions on the number of documents for a factory to
    asssemble for a given `Blueprint`.
    """

    def __init__(self, blueprint, quantity):

        # The blueprint the quota refers to
        self._blueprint = blueprint

        # The quantity of documents to assemble
        self._quantity = quantity

    # Read-only properties

    @property
    def blueprint(self):
        return self._blueprint

    @property
    def quantity(self):
        if isinstance(self._quantity, Quantity):
            return self._quantity()
        return self._quantity
