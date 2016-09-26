"""Interact with online albums."""

from pygur.htget import Meta
from pygur.image import Image
from re import compile as regex
from requests import get


VALID_TAG = regex(r'^\w+$')
NON_WORD = regex(r'[^\w\s\-\_]')
SHRINK = regex(r'[\s-]+')
HTML = 'https://imgur.com/a/%s/layout/blog'


class Error(Exception):
    pass


def protect(f):
    def g(self):
        assert isinstance(self, Album)
        try:
            return f(self)
        except AttributeError:
            self._parse()
            try:
                return f(self)
            except AttributeError:
                raise Error('invalid album')
    return g


class Album:
    """Perform operations on Imgur album."""

    def __init__(self, tag: str):
        """Initialize Album object."""

        if not VALID_TAG.match(tag):
            raise ValueError('invalid tag %r' % tag)

        self._tag = tag
        self._html = HTML % tag

    @property
    def tag(self):
        return self._tag

    # borrow image method
    __repr__ = Image.__repr__

    def _parse(self):
        html = InfoAlbum(get(self._html, stream=True))
        meta = html.all(2**10)

        self._title = meta['og:title']
        self._images = list(map(Image, html.tags))

    @property
    @protect
    def title(self) -> str:
        return self._title

    @property
    @protect
    def images(self) -> list:
        return self._images


class InfoAlbum(Meta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tags = []

    def start_div(self, attrs):
        d = {k: v for k, v in attrs}
        if 'class' in d:
            if 'post-image-container' in d['class']:
                self.tags.append(d['id'])


def main(what=None, program=None):
    from pathlib import Path
    from argparse import ArgumentParser
    from json import dump

    parser = ArgumentParser(prog=program,
                            description='Download albums from Imgur.')
    parser.add_argument('tag', help='Album to download by tag.')
    parser.add_argument('-o', '--output', help='Set output directory.')
    parser.add_argument('-f', '--format', default='%(index)s_%(tag)s.%(ext)s',
                        help='Pattern for file names.')
    parser.add_argument('-s', '--start', default=0, type=int, help='Start index.')
    parser.add_argument('-e', '--end', default=-1, type=int, help='End index.')
    parser.add_argument('-m', '--meta', action='store_true', help='place meta data file in directory')
    args = parser.parse_args(what)

    print(args.tag)

    assert args.start >= 0, 'starting position cannot be less than zero'

    album = Album(args.tag)

    if args.output is None:
        # auto generate neat path
        title = NON_WORD.sub('', album.title)
        title = SHRINK.sub('_', title)
        path = Path(title)
    else:
        path = Path(args.output)

    if not path.exists():
        path.mkdir()

    if args.meta:
        with (path / '.meta').open('w') as file:
            dump({
                'title': album.title,
                'tag': album.tag
            }, file, indent=4)

    count = 0
    for i, img in enumerate(album.images):
        if i < args.start:
            continue
        elif i >= args.end >= 0:
            break

        assert isinstance(img, Image)
        form = {
            'tag': img.tag,
            'index': '0' * (3 - len(str(i))) + str(i),
            'ext': img.extension
        }

        print('Downloading image %r: %s' % (i, img.title))
        img.easy(path / (args.format % form))
        count += 1

    print('Finished downloading %r images.' % count)


if __name__ == '__main__':
    main()
