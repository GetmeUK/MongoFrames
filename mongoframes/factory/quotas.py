
__all__ = ['Quota']


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
        return int(self._quantity)
