from urllib.parse import urlencode

from mongoframes.factory import quotas
from mongoframes.factory.makers import images as image_makers

from tests.fixtures import *


def test_image_url():
    """
    `ImageURL` makers should return the URL for a placeholder image service such
    as `http://fakeimg.pl`.
    """

    # Generate an image URL for the default service provider
    maker = image_makers.ImageURL(
        quotas.Quota(100),
        quotas.Quota(200),
        background='DDDDDD',
        foreground='888888',
        options={'text': 'foo'}
        )

    # Check the assembled result
    image_url = '//fakeimg.pl/100x200/DDDDDD/888888/?text=foo'
    assembled = maker._assemble()
    assert assembled == image_url

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == image_url

    # Configured for a custom service provider
    def placehold_it_formatter(
        service_url,
        width,
        height,
        background,
        foreground,
        options
        ):
        """Generage an image URL for the placehold.it service"""

        # Build the base URL
        image_tmp = '{service_url}/{width}x{height}/{background}/{foreground}'
        image_url = image_tmp.format(
            service_url=service_url,
            width=width,
            height=height,
            background=background,
            foreground=foreground
            )

        # Check for a format option
        fmt = ''
        if 'format' in options:
            fmt = options.pop('format')
            image_url += '.' + fmt

        # Add any other options
        if options:
            image_url += '?' + urlencode(options)

        return image_url

    maker = image_makers.ImageURL(
        quotas.Quota(100),
        quotas.Quota(200),
        background='DDDDDD',
        foreground='888888',
        options={'text': 'foo', 'format': 'png'},
        service_url='//placehold.it',
        service_formatter=placehold_it_formatter
        )

    # Check the assembled result
    image_url = '//placehold.it/100x200/DDDDDD/888888.png?text=foo'
    assembled = maker._assemble()
    assert assembled == image_url

    # Check the finished result
    finished = maker._finish(assembled)
    assert finished == image_url