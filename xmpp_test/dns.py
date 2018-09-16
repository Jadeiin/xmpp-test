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
from typing import List
from typing import Generator
from typing import Union
from typing import AsyncGenerator

import aiodns  # type: ignore

from .constants import Check
from .constants import SRV_TYPE
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

    @property
    def is_xmpps(self) -> bool:
        return self.service == SRV_TYPE.XMPPS_CLIENT.value or self.service == SRV_TYPE.XMPPS_SERVER.value

    async def resolve(self, ip4: bool = True, ip6: bool = True) -> AsyncGenerator['XMPPTarget', None]:
        """Resolve this SRV record to IPv4/IPv6 records in an asynchronous generator."""

        if not ip4 and not ip6:
            raise ValueError("Both IPv4 and IPv6 resolution are disabled.")

        resolver = aiodns.DNSResolver()
        has_ip4 = False
        has_ip6 = False

        if ip4:
            try:
                ip4_records = await resolver.query(self.target, 'A')
                for result in ip4_records:
                    yield XMPPTarget(self, result.host)
                has_ip4 = True
            except aiodns.error.DNSError:
                pass

        if ip6:
            try:
                ip6_records = await resolver.query(self.target, 'AAAA')
                for result in ip6_records:
                    yield XMPPTarget(self, result.host)
                has_ip6 = True
            except aiodns.error.DNSError:
                pass

        if not has_ip4 and not has_ip6:
            tag.error(2, 'SRV-Record %s has no A/AAAA records.' % self.source, 'dns')
        if ip4 and not has_ip4:
            tag.warning(3, 'No IPv6 records for %s' % self.target, 'dns')
        if ip6 and not has_ip6:
            tag.warning(4, 'No IPv6 records for %s' % self.target, 'dns')


class XMPPTarget:
    """A class representing possible connection to an XMPP server.

    A typical XMPP test will run for each available ``XMPPTarget``, testing if any SRV Record or IP address is
    misconfigured.

    Parameters
    ----------

    srv : SRVRecord
    ip : str
    """

    srv: SRVRecord
    ip: Union[IPv4Address, IPv6Address]

    def __init__(self, srv: SRVRecord, ip: str) -> None:
        self.srv = srv
        self.ip = ip_address(ip)

    def __str__(self) -> str:
        return '%s -> %s' % (self.srv, self.ip)

    def __repr__(self) -> str:
        return '<XMPPTarget: %s>' % self

    @property
    def is_xmpps(self) -> bool:
        return self.srv.is_xmpps

    def as_dict(self) -> dict:
        return collections.OrderedDict([
            ('source', self.srv.source),
            ('target', self.srv.target),
            ('ip', str(self.ip)),
            ('port', self.srv.port),
        ])


async def srv_records(service: SRV_TYPE, domain: str) -> List[SRVRecord]:
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

    return [SRVRecord(
        service=service.value, proto=proto, domain=domain,
        ttl=r.ttl, priority=r.priority, weight=r.weight,
        port=r.port, target=r.host
    ) for r in results]


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


async def gen_dns_records(domain, typ: Check = Check.CLIENT,
                          ipv4: bool = True, ipv6: bool = True, xmpps: bool = True):
    for srv_service in get_srv_services(typ, xmpps=xmpps):
        for srv_record in await srv_records(srv_service, domain):
            async for result in srv_record.resolve(ip4=ipv4, ip6=ipv6):
                yield result


async def get_dns_records(domain, typ: Check = Check.CLIENT,
                          ipv4: bool = True, ipv6: bool = True, xmpps: bool = True):
    records = []
    async for record in gen_dns_records(domain, typ, ipv4, ipv6, xmpps):
        records.append(record)
    return records


def dns_test(domain: str, typ: Check = Check.CLIENT,
             ipv4: bool = True, ipv6: bool = True, xmpps: bool = True) -> tuple:
    loop = asyncio.get_event_loop()

    data = loop.run_until_complete(get_dns_records(domain, typ, ipv4, ipv6, xmpps))
    tags = tag.pop_all()

    return data, tags
