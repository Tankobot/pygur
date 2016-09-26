from setuptools import setup
from pygur import __version__


setup(
    name='pygur',
    version=__version__,
    packages=['pygur'],
    url='https://github.com/Tankobot/pygur',
    license='GNU General Public License v3',
    author='Michael Bradley',
    author_email='michael@sigm.io',
    description='Unofficial Python Imgur Utility',
    long_description='Pygur can be used to select and perform operations on Imgur objects using Imgur ids.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Utilities'
    ],
    keywords='unofficial imgur download image album',
    install_requires=['requests'],
    entry_points={'console_scripts': ['pygur = pygur:main']}
)
