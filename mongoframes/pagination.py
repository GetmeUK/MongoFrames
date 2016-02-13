"""
Support for paginating items.
"""

import copy
import math

__all__ = (
    'InvalidPage',
    'Page',
    'Paginator'
    )


class InvalidPage(Exception):
    """
    An error raised when an invalid page is requested.
    """


class Page(object):
    """
    A class to represent one page of items.
    """

    def __init__(self, offset, number, items, next, prev):
        self._offset = offset
        self._number = number
        self._items = list(items)
        self._next = next
        self._prev = prev

    @property
    def items(self):
        return self._items

    @property
    def number(self):
        return self._number

    @property
    def next(self):
        return self._next

    @property
    def prev(self):
        return self._prev

    def offset(self, item):
        """Return the offset for a item"""
        return self._offset + self.items.index(item)

    def populate(self, data):
        """Post populate the page items from a dictionary"""

        # Ensure items are converted to a list
        self._items = list(self._items)

        # Track dud items
        duds = []

        populated_items = []
        for item in self._items:
            if item in data:
                populated_items.append(data[item])
            else:
                duds.append(item)

        self._items = populated_items

        return duds

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        for item in self._items:
            yield item

    def __len__(self):
        return len(self._items)


class Paginator(object):
    """
    A pagination class for slicing items into pages. This class is designed
    to work with Frame classes.
    """

    def __init__(self, cls, filter, filter_args={}, per_page=20):
        self._cls = cls
        self._filter = filter
        self._filter_args = filter_args
        self._items_count = cls.count(self._filter, **self._filter_args)

        self._per_page = per_page
        self._page_count = max(1, int(math.ceil(self._items_count / float(self._per_page))))
        self._page_numbers = range(1, self._page_count + 1)

    @property
    def item_count(self):
        return self._items_count

    @property
    def page_count(self):
        return self._page_count

    @property
    def page_numbers(self):
        return self._page_numbers

    def _get_page(self, page_number):
        if page_number not in self._page_numbers:
            raise InvalidPage(page_number, self.page_count)

        # Calculate the next and previous page numbers
        next = page_number + 1 if page_number + 1 in self._page_numbers else None
        prev = page_number - 1 if page_number - 1 in self._page_numbers else None

        # Select the items for the page
        filter_args = self._filter_args
        filter_args['skip'] = (page_number - 1) * self._per_page
        filter_args['limit'] = self._per_page
        items = self._cls.many(self._filter, **filter_args)

        return Page(
            offset=filter_args['skip'],
            number=page_number,
            items=items,
            next=next,
            prev=prev
            )

    def __getitem__(self, i):
        return self._get_page(i)

    def __iter__(self):
        for page_number in self._page_numbers:
            yield self._get_page(i)