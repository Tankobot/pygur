from .album import Album
from .image import Image


__author__ = 'Michael Bradley <michael@sigm.io>'
__copyright__ = 'GNU General Public License v3'
VERSION = (0, 2, 0)  # semantic version
__version__ = '.'.join(map(str, VERSION))  # "major.minor.patch"


def main():
    from argparse import ArgumentParser
    from sys import argv

    parser = ArgumentParser(prog='pygur', description='Unofficial Python Imgur Utility')
    parser.add_argument('mode', help='operation mode: image or album')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__,
                        help='display version information and exit')
    args = parser.parse_args(argv[1:2])

    # remove program and mode
    n_args = argv[2:]

    if args.mode == 'image':
        from pygur.image import main
        main(n_args, 'pygur image')
    elif args.mode == 'album':
        from pygur.album import main
        main(n_args, 'pygur album')
    else:
        parser.error('invalid mode')


if __name__ == '__main__':
    main()
