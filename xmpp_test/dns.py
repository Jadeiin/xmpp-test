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
from typing import List
from typing import Union

import aiodns

from .constants import SRV_XMPPS_CLIENT
from .constants import SRV_XMPPS_SERVER
from .constants import SRV_XMPP_CLIENT
from .constants import SRV_XMPP_SERVER


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

    def __str__(self) -> str:
        return '_%s._%s.%s -> %s:%s' % (self.service, self.proto, self.domain, self.target, self.port)

    def __repr__(self) -> str:
        return '<SRVRecord: %s>' % self

    async def resolve(self) -> List[Union[IPv4Address, IPv6Address]]:
        resolver = aiodns.DNSResolver()
        has_records = False

        try:
            ip4_records = await resolver.query(self.target, 'A')
            for result in ip4_records:
                print(dir(result))
                yield result
            has_records = True
        except aiodns.error.DNSError:
            pass

        try:
            ip6_records = await resolver.query(self.target, 'AAAA')
            for result in ip6_records:
                yield result
            has_records = True
        except aiodns.error.DNSError:
            pass

        if has_records is False:
            raise RuntimeError('No Records for this SRV record!')


async def srv_records(service, domain, proto='tcp'):
    resolver = aiodns.DNSResolver()
    query = '_%s._%s.%s' % (service, proto, domain)
    results = await resolver.query(query, 'SRV')
    return [SRVRecord(
        service=service, proto=proto, domain=domain,
        ttl=r.ttl, priority=r.priority, weight=r.weight,
        port=r.port, target=r.host
    ) for r in results]


async def xmpp_client_records(domain):
    for srv in await srv_records(SRV_XMPP_CLIENT, domain):
        yield srv
    for srv in await srv_records(SRV_XMPPS_CLIENT, domain):
        yield srv


async def xmpp_server_records(domain):
    for srv in await srv_records(SRV_XMPP_SERVER, domain):
        yield srv
    for srv in await srv_records(SRV_XMPPS_SERVER, domain):
        yield srv


async def test2(domain, service=SRV_XMPPS_CLIENT):
    for srv in await srv_records(service, domain):
        async for result in srv.resolve():
            print('result: %s' % (result, ))
