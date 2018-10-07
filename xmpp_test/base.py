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
from ipaddress import IPv4Address
from ipaddress import IPv6Address
from ipaddress import ip_address
from typing import AsyncGenerator
from typing import Generator
from typing import List
from typing import Union

import aiodns

from .constants import SRV_TYPE
from .constants import Check
from .tags import tag


class SRVRecord:
    """A class representing a generic SRV record.

    Parameters
    ----------

    service : str
        Symbolic name of the desired service (e.g. ``"xmpp-client"``).
    proto : str
        The transport protocol of the desired service (e.g. ``"tcp"``).
    domain : str
        The domain name for which this record is valid (e.g. "``example.com``").
    ttl : int
        TTL for the DNS record.
    priority : int
        Priority for the DNS record.
    weight : int
        Weight for the DNS record.
    port : int
        TCP  or UDP port on which this service can be found.
    target : str
        The target domain for this service (e.g. ``"xmpp.example.com"``).
    """
    service: str
    proto: str
    domain: str
    ttl: int
    priority: int
    weight: int
    port: int
    target: str

    def __init__(self, service: str, proto: str, domain: str, ttl: int, priority: int, weight: int, port: int,
                 target: str) -> None:
        self.service = service
        self.proto = proto
        self.domain = domain
        self.ttl = ttl
        self.priority = priority
        self.weight = weight
        self.port = port
        self.target = target

    @property
    def source(self) -> str:
        """Returns the DNS name of this record, e.g. ``"_xmpp-client._tcp.example.com"``."""
        return '_%s._%s.%s' % (self.service, self.proto, self.domain)

    def __str__(self) -> str:
        return '%s -> %s:%s' % (self.source, self.target, self.port)

    def __repr__(self) -> str:
        return '<SRVRecord: %s>' % self

    @classmethod
    async def srv_records(cls, service: SRV_TYPE, domain: str) -> List['SRVRecord']:
        """Return list of SRV records for the given SRV type and for the given domain.

        Parameters
        ----------

        service : SRV_TYPE
            One of the SRV_TYPE constants designating the desired XMPP service.
        domain : str
            The Domain to test.
        """
        proto = 'tcp'
        resolver = aiodns.DNSResolver()
        query = '_%s._%s.%s' % (service.value, proto, domain)
        try:
            results = await resolver.query(query, 'SRV')
        except aiodns.error.DNSError as e:
            tag.error(0, 'No SRV record "%s" for domain %s' % (query, domain), 'dns')
            return []

        return [cls(
            service=service.value, proto=proto, domain=domain,
            ttl=r.ttl, priority=r.priority, weight=r.weight,
            port=r.port, target=r.host
        ) for r in results]

    @property
    def is_xmpps(self) -> bool:
        return self.service == SRV_TYPE.XMPPS_CLIENT.value or self.service == SRV_TYPE.XMPPS_SERVER.value


class XMPPTarget:
    srv: SRVRecord
    ip: Union[IPv4Address, IPv6Address]

    def __init__(self, srv: SRVRecord, ip: str) -> None:
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

    @classmethod
    async def from_srv_record(cls, srv_record: SRVRecord, ip4: bool = True,
                              ip6: bool = True) -> AsyncGenerator['XMPPTarget', None]:
        """Resolve this SRV record to IPv4/IPv6 records in an asynchronous generator."""

        if not ip4 and not ip6:
            raise ValueError("Both IPv4 and IPv6 resolution are disabled.")

        resolver = aiodns.DNSResolver()
        has_ip4 = False
        has_ip6 = False

        if ip4:
            try:
                ip4_records = await resolver.query(srv_record.target, 'A')
                for result in ip4_records:
                    yield cls(srv_record, result.host)
                has_ip4 = True
            except aiodns.error.DNSError:
                pass

        if ip6:
            try:
                ip6_records = await resolver.query(srv_record.target, 'AAAA')
                for result in ip6_records:
                    yield cls(srv_record, result.host)
                has_ip6 = True
            except aiodns.error.DNSError:
                pass

        if not has_ip4 and not has_ip6:
            tag.error(2, 'SRV-Record %s has no A/AAAA records.' % srv_record.source, 'dns')
        if ip4 and not has_ip4:
            tag.warning(3, 'No IPv6 records for %s' % srv_record.target, 'dns')
        if ip6 and not has_ip6:
            tag.warning(4, 'No IPv6 records for %s' % srv_record.target, 'dns')

    @classmethod
    async def from_domain(cls, domain, typ: Check = Check.CLIENT,
                          ipv4: bool = True, ipv6: bool = True, xmpps: bool = True):
        for srv_service in get_srv_services(typ, xmpps=xmpps):
            for srv_record in await SRVRecord.srv_records(srv_service, domain):
                async for target in cls.from_srv_record(srv_record, ip4=ipv4, ip6=ipv6):
                    yield target


def get_srv_services(typ: Check, xmpps: bool = True) -> Generator[SRV_TYPE, None, None]:
    """Get the desired XMPP services.

    Parameters
    ----------

    typ : Check
        Wether to test the client or server side.
    xmpps : bool, optional
        Set to False to exclude XEP-0368 style SRV records.
    """
    if typ == Check.CLIENT:
        yield SRV_TYPE.XMPP_CLIENT
        if xmpps is True:
            yield SRV_TYPE.XMPPS_CLIENT

    elif typ == Check.SERVER:
        yield SRV_TYPE.XMPP_SERVER
        if xmpps is True:
            yield SRV_TYPE.XMPPS_CLIENT

    else:
        raise ValueError("Unknown check type: %s" % typ)


class Test:
    def __init__(self, *args, **kwargs):
        self.loop = asyncio.get_event_loop()

        self.args = args
        self.kwargs = kwargs

    def test(self, *args, **kwargs):  # equivalent to start
        data = self.loop.run_until_complete(self.run(*args, **kwargs))
        tags = tag.pop_all()
        return data, tags

    def start(self):
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(self.run(*self.args, **self.kwargs))
        tags = tag.pop_all()
        return data, tags

    async def run(self, *args, **kwargs):
        """To be implemented."""
        pass


class XMPPTargetTest(Test):
    def get_tests(self, domain, target):
        yield {}

    async def run(self, domain: str, typ: Check = Check.CLIENT,
                  ipv4: bool = True, ipv6: bool = True, xmpps: bool = True) -> tuple:

        futures = []
        async for target in XMPPTarget.from_domain(domain, typ, ipv4, ipv6, xmpps):
            for test_kwargs in self.get_tests(domain, target):
                futures.append(asyncio.ensure_future(self.target_test(target, **test_kwargs)))
        return await asyncio.gather(*futures)


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

    def json(self):
        return self.as_dict()
