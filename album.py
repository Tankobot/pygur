"""Interact with online albums."""

from re import compile as regex
from image import Image


VALID_TAG = regex(r'^\w+$')
HTML = 'https://imgur.com/a/%s/layout/blog'


class Error(Exception):
    pass


class Album:
    """Perform operations on Imgur album."""

    def __init__(self, tag: str):
        """Initialize Album object."""

        if not VALID_TAG.match(tag):
            raise ValueError('invalid tag %r' % tag)

        self._tag = tag
        self._html = HTML % tag
