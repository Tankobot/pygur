"""Interact with online images."""

from re import compile as regex
from io import FileIO
from typing import Union
from collections import namedtuple
from pathlib import Path
import requests
from visual import progress_bar
from htget import MetaGet


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
        self._meta = None  # metadata can be retrieved later

    META = []  # type: list[property]

    @property
    def tag(self):
        return self._tag

    @property
    def meta(self) -> dict:
        """Retrieve metadata from Imgur."""
        if self._meta:
            return self._meta
        else:
            mask = {'User-Agent': 'Mozilla/5.0 Firefox/48.0'}  # spoof user-agent
            response = requests.get(self._html, headers=mask, stream=True)
            self._meta = MetaGet(response).all(2 ** 10)

            try:
                for p in self.META:
                    p.fget()
            except KeyError:
                raise Error('unable to get metadata %r' % self._tag) from None

            return self._meta

    @property
    def keywords(self) -> list:
        """List of the image's keywords."""
        return self.meta['keywords'].split(', ')
    META.append(keywords)

    @property
    def description(self) -> str:
        """Imgur image description."""
        return self.meta['description']
    META.append(description)

    @property
    def copyright(self) -> str:
        """Imgur copyright notice."""
        return self.meta['copyright']
    META.append(copyright)

    @property
    def url(self) -> str:
        """Html link provided by Imgur."""
        return self.meta['og:url']
    META.append(url)

    @property
    def title(self) -> str:
        """Imgur image title."""
        return self.meta['og:title']
    META.append(title)

    @property
    def author(self) -> str:
        """Imgur image author."""
        return self.meta['article:author']
    META.append(author)

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

    def save(self, file: FileIO, close=False):
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
        for chunk in r.iter_content(2**10):
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
                'author': self.author,
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
