from urllib.parse import urlencode

from mongoframes.factory.makers import Maker

__all__ = [
    'ImageURL'
    ]


class ImageURL(Maker):
    """
    Return a fake image URL (by default we use the http://fakeimg.pl service).
    """

    def __init__(self,
        width,
        height,
        options=None,
        service_url='http://fakeimg.pl',
        service_formatter=None
        ):

        # The size of the image to generate
        self._width = width
        self._height = height

        # A dictionary of options used when generating the image
        self._options = options

        # The service URL to use when calling the service
        self._service_url = service_url

        # A formatter function that can produce an image URL for the service
        self._service_formatter = service_formatter or \
                ImageURL._default_service_formatter

    def _assemble(self):
        return self._service_formatter(
            self._service_url,
            int(self._width),
            int(self._height),
            self._options
            )

    def _finish(self, value):
        min_date = self.parse_date_obj(self._min_date)
        max_date = self.parse_date_obj(self._max_date)
        seconds = random.randint(0, int((max_date - min_date).total_seconds()))
        return min_date + datetime.timedelta(seconds=seconds)

    @staticmethod
    def _default_service_formatter(service_url, width, height, options):
        """Generate an image URL for a service"""

        # Build the base URL
        image_url = '{service_url}/{width}x{height}/'.format(
            service_url=service_url,
            width=width,
            height=height
            )

        # Add any options
        if options:
            image_url += '?' + urlencode(options)

        return image_url
