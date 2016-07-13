"""
Support for paginating frames.
"""

from copy import deepcopy
import math

from mongoframes.queries import Condition, Group, to_refs


__all__ = (
    # Exceptions
    'InvalidPage',

    # Classes
    'Page',
    'Paginator'
    )


class InvalidPage(Exception):
    """
    An error raised when an invalid page is requested.
    """


class Page(object):
    """
    A class to represent one page of results.
    """

    def __init__(self, offset, number, items, next, prev):

        # The offset of the first result in the page from the first result of
        # the entire selection.
        self._offset = offset

        # The page number
        self._number = number

        # The results/frames for this page
        self._items = list(items)

        # The next and previous page numbers (if there is no next/previous page
        # the value will be None.
        self._next = next
        self._prev = prev

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        for item in self._items:
            yield item

    def __len__(self):
        return len(self._items)

    # Read-only properties

    @property
    def items(self):
        """Return a list of results for the page"""
        return self._items

    @property
    def next(self):
        """
        Return the page number for the next page or None if there isn't one.
        """
        return self._next

    @property
    def number(self):
        """Return the page number"""
        return self._number

    @property
    def prev(self):
        """
        Return the page number for the previous page or None if there isn't one.
        """
        return self._prev

    # Public methods

    def offset(self, item):
        """Return the offset for an item in the page"""
        return self._offset + self.items.index(item)


class Paginator(object):
    """
    A pagination class for slicing query results into pages. This class is
    designed to work with Frame classes.
    """

    def __init__(
            self,
            frame_cls,
            filter=None,
            per_page=20,
            orphans=0,
            **filter_args
            ):

        # The frame class results are being paginated for
        self._frame_cls = frame_cls

        # The filter applied when selecting results from the database (we
        # flattern the filter at this point which effectively deep copies.
        if isinstance(filter, (Condition, Group)):
            self._filter = filter.to_dict()
        else:
            self._filter = to_refs(filter)

        # Any additional filter arguments applied when selecting results such as
        # sort and projection,
        self._filter_args = filter_args

        # The number of results that will be displayed per page
        self._per_page = per_page

        # If a value is specified for orphans then the last page will be able to
        # hold the additional results (up to the value of orphans). This can
        # help prevent users being presented with pages contain only a few
        # results.
        self._orphans = orphans

        # Count the total results being paginated
        self._items_count = frame_cls.count(self._filter)

        # Calculated the number of pages
        total = self._items_count - orphans
        self._page_count = max(1, int(math.ceil(total / float(self._per_page))))

        # Create a list of page number that can be used to navigate the results
        self._page_numbers = range(1, self._page_count + 1)

    def __getitem__(self, page_number):
        if page_number not in self._page_numbers:
            raise InvalidPage(page_number, self.page_count)

        # Calculate the next and previous page numbers
        next = page_number + 1 if page_number + 1 in self._page_numbers else None
        prev = page_number - 1 if page_number - 1 in self._page_numbers else None

        # Select the items for the page
        filter_args = deepcopy(self._filter_args) or {}
        filter_args['skip'] = (page_number - 1) * self._per_page
        filter_args['limit'] = self._per_page

        # Check to see if we need to account for orphans
        if self.item_count - (page_number * self._per_page) <= self.orphans:
            filter_args['limit'] += self.orphans

        # Select the results for the page
        items = self._frame_cls.many(self._filter, **filter_args)

        # Build the page
        return Page(
            offset=filter_args['skip'],
            number=page_number,
            items=items,
            next=next,
            prev=prev
            )

    def __iter__(self):
        for page_number in self._page_numbers:
            yield self[page_number]

    # Read-only properties

    @property
    def item_count(self):
        """Return the total number of items being paginated"""
        return self._items_count

    @property
    def orphans(self):
        """
        Return the number of orphan results that will be allowed in the last
        page of results.
        """
        return self._orphans

    @property
    def page_count(self):
        """Return the total number of pages"""
        return self._page_count

    @property
    def page_numbers(self):
        """Return a list of page numbers"""
        return self._page_numbers

    @property
    def per_page(self):
        """
        Return the number of results per page (with the exception of orphans).
        """
        return self._per_page