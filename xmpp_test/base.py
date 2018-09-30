# This file is part of xmpp-test (https://github.com/mathiasertl/xmpp-test).
#
# xmpp-test is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# xmpp-test is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along with xmpp-test.  If not, see
# <http://www.gnu.org/licenses/>.

import asyncio
import collections
from typing import Union
from ipaddress import IPv4Address
from ipaddress import IPv6Address
from ipaddress import ip_address

from .constants import Check
from .tags import tag


class XMPPTarget:
    srv: 'SRVRecord'
    ip: Union[IPv4Address, IPv6Address]

    def __init__(self, srv: 'SRVRecord', ip: str) -> None:
        self.srv = srv
        self.ip = ip_address(ip)

    @property
    def is_ip4(self) -> bool:
        """True if this test uses IPv4."""
        return isinstance(self.ip, IPv4Address)

    @property
    def is_ip6(self) -> bool:
        """True if this test uses IPv6."""
        return isinstance(self.ip, IPv6Address)

    @property
    def is_xmpps(self) -> bool:
        """Wether or not this test uses XEP-0368 style XMPPS."""

        return self.srv.is_xmpps


class Test:
    def __init__(self, args=None, kwargs=None):
        self.loop = asyncio.get_event_loop()

        self.args = args or tuple()
        self.kwargs = kwargs or dict()

    def test(self, *args, **kwargs):  # equivalent to start
        data = self.loop.run_until_complete(self.run(*args, **kwargs))
        tags = tag.pop_all()
        return data, tags

    async def run(self, *args, **kwargs):
        """To be implemented."""
        pass


class TestResult:
    """Base class for test results.

    This class only contains the actual connection parameters that this test used: The SRV record and the IP
    address it resolved to.

    Parameters
    ----------

    srv : SRVRecord
    ip : str
    """

    target: XMPPTarget
    success: bool

    def __init__(self, target: XMPPTarget, success: bool) -> None:
        self.target = target
        self.success = success

    def __str__(self) -> str:
        return '%s -> %s' % (self.srv, self.ip)

    def __repr__(self) -> str:
        return '<%s: %s>' % (self.__class__.__name__, self)

    def as_dict(self) -> dict:
        return collections.OrderedDict([
            ('source', self.target.srv.source),
            ('target', self.target.srv.target),
            ('ip', str(self.target.ip)),
            ('port', self.target.srv.port),
            ('success', self.success),
        ])

    def tabulate(self):
        d = self.as_dict()
        d['status'] = 'working' if d.pop('success') else 'failed'
        return d
