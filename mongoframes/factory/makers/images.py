from urllib.parse import urlencode

from mongoframes.factory.makers import Maker

__all__ = [
    'ImageURL'
    ]


class ImageURL(Maker):
    """
    Return a fake image URL (by default we use the `fakeimg.pl` service).
    """

    def __init__(self,
        width,
        height,
        background='CCCCCC',
        foreground='8D8D8D',
        options=None,
        service_url='//fakeimg.pl',
        service_formatter=None
        ):
        super().__init__()

        # The size of the image to generate
        self._width = width
        self._height = height

        # The foreground/background colours for the image
        self._background = background
        self._foreground = foreground

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
            self._background,
            self._foreground,
            self._options
            )

    @staticmethod
    def _default_service_formatter(
        service_url,
        width,
        height,
        background,
        foreground,
        options
        ):
        """Generate an image URL for a service"""

        # Build the base URL
        image_tmp = '{service_url}/{width}x{height}/{background}/{foreground}/'
        image_url = image_tmp.format(
            service_url=service_url,
            width=width,
            height=height,
            background=background,
            foreground=foreground
            )

        # Add any options
        if options:
            image_url += '?' + urlencode(options)

        return image_url
