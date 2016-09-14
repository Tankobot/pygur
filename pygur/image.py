"""Interact with online images."""

from pygur.visual import progress_bar
from pygur.htget import Meta
from re import compile as regex
import requests
from collections import namedtuple
from io import FileIO
from pathlib import Path
from typing import Union, List


VALID_TAG = regex(r'^\w+$')
EXTENSION = regex(r'\.\w+$')  # check metadata for file extension
HTML = 'https://imgur.com/%s'
SOURCE = 'https://i.imgur.com/%s.png'  # any file extension will work


Resolution = namedtuple('Resolution', 'x y')


class Error(Exception):
    pass


class Image:
    """Perform operations on one Imgur image."""

    def __init__(self, tag: str):
        if not VALID_TAG.match(tag):
            raise ValueError('invalid tag %r' % tag)

        self._tag = tag
        self._html = HTML % tag
        self._source = SOURCE % tag

        # get metadata
        response = requests.get(self._html, headers=self.mask, stream=True)
        self.meta = Meta(response).all(2 ** 10)

        try:
            # make sure all required metadata is present
            for p in self.META:
                p.fget()
        except KeyError as e:
            raise Error('unable to get metadata (%s) from %r' % (e.args[0], tag)) from None

    # help ensure correct html response
    mask = {'User-Agent': 'Mozilla/5.0 Firefox/48.0'}
    # track required metadata
    META = []  # type: List[property]

    @property
    def tag(self):
        return self._tag

    @property
    def title(self) -> str:
        """Imgur image title."""
        return self.meta['og:title']
    META.append(title)

    @property
    def resolution(self) -> Resolution:
        """Resolution of the image."""
        x = int(self.meta['og:image:width'])
        y = int(self.meta['og:image:height'])
        return Resolution(x, y)
    META.append(resolution)

    @property
    def extension(self) -> str:
        """Image file extension not including period prefix."""
        return EXTENSION.search(self.meta['twitter:image']).group(0)[1:]
    META.append(extension)

    # url might be unnecessary, consider removal
    @property
    def url(self) -> str:
        """Html link provided by Imgur."""
        return self.meta['og:url']
    META.append(url)

    def save(self, file: FileIO, close=False, chunk_size=2**10):
        """Write the image from Imgur to a file object."""

        r = requests.get(self._source, stream=True)

        # attempt to retrieve image size
        try:
            size = int(r.headers['content-length'])
            pro = True
        except KeyError:
            size = 0
            pro = False
        done = 0

        # download image and return progress
        for chunk in r.iter_content(chunk_size):
            file.write(chunk)
            done += len(chunk)
            yield done / size if pro else 1

        # close file at end of write automatically
        if close:
            file.close()

    def to_file(self, place: Union[Path, str] = None, meta=False, pro=False):
        """Save image directly to a file."""

        if place is None:
            # automatic location
            meta = True
            place = '%(title)s_%(x)sx%(y)s_%(tag)s.%(ext)s'

        if meta:
            meta = {
                'tag': self.tag,
                'title': self.title,
                'x': self.resolution.x,
                'y': self.resolution.y,
                'ext': self.extension
            }

        if isinstance(place, str):
            place = Path(place % meta)

        if pro:
            print('Saving %s' % place)

        return self.save(place.open('wb'), close=True)

    def easy(self, place: str = None, meta=None):
        """Evaluate generator."""

        progress_bar(self.to_file(place, meta, pro=True))
        print('Image saved.')


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Download images from Imgur.')
    parser.add_argument('tags', nargs='+', help='Images to download by tag.')
    parser.add_argument('-o', '--output', default='', help='Set output directory.')
    args = parser.parse_args()

    for tag in args.tags:
        if not VALID_TAG.match(tag):
            raise ValueError('invalid tag %r' % tag)

    for tag in args.tags:
        try:
            Image(tag).easy(str(Path(args.output) / '%(tag)s.%(ext)s'), meta=True)
        except Error as e:
            print('Error: %s' % e)


if __name__ == '__main__':
    main()
