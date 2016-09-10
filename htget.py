"""Collect html page meta data."""

import requests
from html.parser import HTMLParser
from collections import namedtuple


AttPair = namedtuple('AttPair', 'name value')


class Getter(HTMLParser):
    """Translate the head section of an html document into a dictionary."""

    def __init__(self, response: requests.Response):
        super().__init__()
        self._response = response
        self.state = None

    @staticmethod
    def pairs(attrs):
        return [AttPair(*at) for at in attrs]

    def handle_starttag(self, tag, attrs):
        if hasattr(self, 'start_' + tag):
            getattr(self, 'start_' + tag)(self.pairs(attrs))

    def handle_data(self, data):
        if hasattr(self, 'data_' + self.state):
            getattr(self, 'data_' + self.state)(data)

    def handle_endtag(self, tag):
        if hasattr(self, 'end_' + tag):
            getattr(self, 'end_' + tag)()

    def all(self, chunk_size: int) -> dict:
        for chunk in self._response.iter_content(chunk_size, True):
            self.feed(chunk)
            if not self._head:
                break
        return self.meta

    def error(self, message):
        pass


class Meta(Getter):
    def __init__(self, response: requests.Response):
        super().__init__(response)
        self.meta = {}  # type: dict[str]
        self._head = True

    def start_meta(self, a: list[AttPair]):
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
