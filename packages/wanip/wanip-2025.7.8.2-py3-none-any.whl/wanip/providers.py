"""Wrap 'public providers for WANIP' in a data structure with convenience operations

It is really our interpretation that those be labelled thusly...
"""

import random
from typing import Iterator, Any, Self

from lsattr import LsAttr

__all__ = [
    'Public_Providers',
    'Providers',
]

class Providers(LsAttr):

    def __init__(self, *providers, use_cached=False, cached=None):
        """Store the providers in a tuple

        This feels more natural than, say, a list or a set; although we will resort to the former
        and emulate semantix of the latter below.
        """
        self.providers = tuple(providers)
        self.use_cached = use_cached
        self.cached = cached

    def __call__(self, use_cached=False):
        """Gimme any one"""

        if not use_cached:
            try:
                assert len(self.providers) >= 1
            # We catch TypeError in case we have left the context: len(None)...
            except (AssertionError, TypeError) as exc:
                raise ValueError('no element found in collection') from exc

            self.cached = random.choice(self.providers)
            return self.cached
        else:
            try:
                assert self.cached is not None
                return self.cached
            except AssertionError as exc:
                raise ValueError('no element found in cache') from exc

    def __add__(self, provider):
        """Augment the collection

        As tuples are immutable, we temporarily escape to lists.  We do not allow an element to be
        added more than once.
        """
        try:
            assert provider not in self.providers
        except AssertionError as exc:
            raise ValueError(f'"{provider}" is already part of the collection') from exc

        _l = list(self.providers)
        _l.append(provider)
        return self.__class__(*(_p for _p in _l), use_cached=self.use_cached, cached=self.cached)

    def __sub__(self, provider):
        """Diminish the collection

        Again, we resort to lists while doing the job.
        """
        _l = list(self.providers)

        try:
            _l.remove(provider)
        except ValueError as exc:
            raise ValueError(f'"{provider}" is not part of the collection') from exc

        return self.__class__(*(_p for _p in _l), use_cached=self.use_cached, cached=self.cached)

    def __len__(self):
        """Tell the size of the collection"""

        return len(self.providers)

    def __contains__(self, provider):
        """Test for membership

        We waive the "in" operator so that we can re-use the iterator.
        """
        for _candidate in self:
            if _candidate == provider:
                return True
        return False

    def __iter__(self) -> Iterator[Any]:
        """Make the collection iterable/usable in generators"""

        for _p in self.providers:
            yield _p

    def __str__(self):
        """Pretty-print"""

        return '\n'.join(sorted(str(provider) for provider in self))

    def __enter__(self) -> Self:
        """Enter context"""

        return self

    def __exit__(self, exc_value, exc_type, traceback):
        """Leave context"""

        self.providers = None
        self.cached    = None
        return False

# Export this
Public_Providers = Providers(
    'https://ifconfig.me/ip',
    'https://my.ip.fi',
    'https://icanhazip.com',
    'https://ifconfig.co',
    'https://ipecho.net/plain',
    'https://ipinfo.io/ip',
    'https://ident.me',
    'https://iprs.fly.dev',
    'https://l2.io/ip',
    'https://ipapi.co/ip',
    'https://wgetip.com',
    'https://whatismyip.akamai.com',
    'https://eth0.me/',
    'https://api.ipify.org',
    'https://ip.me',
    'https://checkip.amazonaws.com',
    'https://www.trackip.net/ip',
)
