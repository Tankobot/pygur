"""Make interpreter commands more appealing."""

from _collections_abc import Iterable, Callable
from numbers import Number


def limit(n: Number, low: Number, high: Number):
    return max(low, min(high, n))


def progress_bar(iterable: Iterable, width=60, form=':%s:'):
    def get_bar(per: float):
        per = limit(per, 0, width)
        bar = '=' * int(per * width)
        bar += '-' if per % 1 >= 0.5 else ''
        bar += ' ' * (width - len(bar))
        return form % bar

    for pro in iterable:
        print(get_bar(pro), end='\r')
    print(get_bar(1))


class Progress:
    def __init__(self, func: Callable):
        self._func = func

    def __call__(self, *args, **kwargs):
        progress_bar(self._func(*args, **kwargs))
