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
import socket
from typing import List
from typing import Tuple

from .constants import Check
from .dns import gen_dns_records
from .tags import tag
from .dns import XMPPTarget


class SocketTestResult:
    target: XMPPTarget
    successful: bool

    def __init__(self, target: XMPPTarget, successful: bool) -> None:
        self.target = target
        self.successful = successful

    def as_dict(self) -> dict:
        d = self.target.as_dict()
        d['status'] = self.successful
        return d

    def tabulate(self) -> dict:
        d = self.as_dict()
        d['status'] = 'working' if d['status'] else 'failed'
        return d


async def test_socket(target: XMPPTarget) -> Tuple[XMPPTarget, bool]:
    ip = str(target.ip)
    port = target.srv.port

    s = socket.socket()
    s.settimeout(2)

    loop = asyncio.get_event_loop()
    try:
        await loop.sock_connect(s, (ip, port))
        return target, True
    except Exception as e:
        return target, False


async def run_socket_test(domain: str, typ: Check = Check.CLIENT,
                          ipv4: bool = True, ipv6: bool = True, xmpps: bool = True
                          ) -> List[SocketTestResult]:

    futures = []
    async for target in gen_dns_records(domain, typ, ipv4, ipv6, xmpps):
        futures.append(asyncio.ensure_future(test_socket(target)))
    return [SocketTestResult(t, s) for t, s in await asyncio.gather(*futures)]


def socket_test(domain: str, typ: Check = Check.CLIENT,
                ipv4: bool = True, ipv6: bool = True, xmpps: bool = True) -> tuple:
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(run_socket_test(domain, typ, ipv4, ipv6, xmpps))
    tags = tag.pop_all()
    return data, tags
