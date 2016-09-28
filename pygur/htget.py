"""Collect html page meta data."""

from logging import getLogger, NullHandler
import requests
from html.parser import HTMLParser
from collections import namedtuple
from typing import List, Dict


log = getLogger(__name__)
log.addHandler(NullHandler())
AttPair = namedtuple('AttPair', 'name value')


class Error(Exception):
    pass


class Getter(HTMLParser):
    """Translate the head section of an html document into a dictionary."""

    def __init__(self, response: requests.Response):
        """Initialize html getter."""
        log.debug('html getter bound to %r', response)
        super().__init__()
        self._response = response
        self._element = ['']
        self._next = None

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._response)

    @property
    def tree(self):
        return '.'.join(self._element)

    @property
    def state(self) -> str:
        """Return the current element."""
        return self._element[-1]

    @state.setter
    def state(self, value: str):
        """Add or remove new state to or from the element stack."""
        if value is None:
            self._element.pop()
        else:
            self._element.append(value)

    @staticmethod
    def pairs(attrs):
        """Convert default html attribute tuple pairs to namedtuple attributes."""
        return [AttPair(*at) for at in attrs]

    def _at(self, prefix: str, tag: str):
        return getattr(self, prefix + tag)

    def start(self, tag, attrs):
        return self._at('start_', tag)(self.pairs(attrs))

    def data(self, tag, data):
        return self._at('data_', tag)(data)

    def end(self, tag):
        return self._at('end_', tag)()

    def handle_starttag(self, tag, attrs):
        """Pass start tag to proper function."""
        if hasattr(self, 'start_' + tag):
            self.start(tag, attrs)
            self.state = tag
            log.debug('start tag %s', self.tree)

    def handle_data(self, data):
        """Pass data to proper function."""
        if hasattr(self, 'data_' + self.state):
            log.debug('data tag %s', self.tree)
            self.data(self.state, data)

    def handle_endtag(self, tag):
        """Pass end tag to proper function."""
        if hasattr(self, 'end_' + tag):
            self.end(tag)
            self.state = None
            log.debug('end tag %s', self.tree)

    def all(self, chunk_size: int):
        """Process entire response and finish html parser."""
        log.debug('handling entire html response %r', self)
        for chunk in self._response.iter_content(chunk_size, True):
            self.feed(chunk)
        self._response.close()
        self.close()
        log.debug('finished html response %r', self)

    def error(self, message):
        raise Error(message)


class Meta(Getter):
    """Collect info from meta tags into dictionary."""

    def __init__(self, response: requests.Response):
        super().__init__(response)
        self.meta = {}  # type: Dict[str]

    def start_meta(self, a: List[AttPair]):
        """Retrieve meta pairs from meta elements."""

        name = None
        value = None

        for pair in a:
            if pair.name in {
                'name',
                'property'
            }:
                name = pair.value  # type: str
            elif pair.name == 'content':
                value = pair.value  # type: str

        if name and value:
            self.meta[name.lower()] = value

    def all(self, chunk_size: int) -> dict:
        """Return complete metadata."""
        super().all(chunk_size)
        return self.meta
