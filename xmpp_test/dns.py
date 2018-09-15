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

from ipaddress import IPv4Address
from ipaddress import IPv6Address
from ipaddress import ip_address
from typing import List
from typing import Union
from typing import AsyncGenerator

import aiodns  # type: ignore

from .constants import Check
from .constants import SRV_TYPE
from .tags import tag


class SRVRecord:
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
        return '_%s._%s.%s' % (self.service, self.proto, self.domain)

    def __str__(self) -> str:
        return '%s -> %s:%s' % (self.source, self.target, self.port)

    def __repr__(self) -> str:
        return '<SRVRecord: %s>' % self

    async def resolve(self) -> AsyncGenerator[List[Union[IPv4Address, IPv6Address]], None]:
        resolver = aiodns.DNSResolver()
        has_ip4 = False
        has_ip6 = False

        try:
            ip4_records = await resolver.query(self.target, 'A')
            for result in ip4_records:
                yield XMPPTarget(self, result.host)
            has_ip4 = True
        except aiodns.error.DNSError:
            pass

        try:
            ip6_records = await resolver.query(self.target, 'AAAA')
            for result in ip6_records:
                yield XMPPTarget(self, result.host)
            has_ip6 = True
        except aiodns.error.DNSError:
            pass

        if not has_ip4 and not has_ip6:
            tag.error(2, 'SRV-Record %s has no A/AAAA records.' % self.source, 'dns')
        elif not has_ip4:
            tag.warning(1, 'No IPv6 records for %s' % self.source, 'dns')
        elif not has_ip6:
            tag.warning(1, 'No IPv6 records for %s' % self.source, 'dns')


class XMPPTarget:
    """A class representing possible connection to an XMPP server.

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


async def srv_records(service: SRV_TYPE, domain: str, proto: str = 'tcp') -> List[SRVRecord]:
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


def get_srv_services(typ: Check, xmpps: bool) -> List[SRV_TYPE]:
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


async def get_dns_records(domain, typ: Check = Check.CLIENT,
                          ipv4: bool = True, ipv6: bool = True, xmpps: bool = True):
    records = []
    for srv_service in get_srv_services(typ, xmpps):
        for srv_record in await srv_records(srv_service, domain):
            async for result in srv_record.resolve():
                records.append(result)

    return records
