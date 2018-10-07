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
#from .dns import gen_dns_records
from .tags import tag
from .base import XMPPTarget
from .base import TestResult


class SocketTestResult(TestResult):
    """A test result for a socket test."""

    pass


async def test_single_socket(target: XMPPTarget) -> Tuple[XMPPTarget, bool]:
    """Asynchronous function to test a single XMPPTarget.

    Parameters
    ----------

    target : XMPPTarget
        The target to test.

    Returns
    -------

    target : XMPPTarget
        The same target that was passed to this function.
    success : bool
        If the test was successful or not.
    """
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
    """Test all configured XMPP SRV records by doing a basic socket connection.

    This test has nothing to do with XMPP connections yet.

    Parameters
    ----------

    domain : str
        The domain to test.
    check : Check
        Wether to check XMPP client or server connections.
    ip4: bool, optional
        Wether or not to test IPv4 connections.
    ip6 : bool, optional
        Wether or not to test IPv6 connections.
    xmpps : bool, optional
        Wether or not to test XEP-0368 style XMPPS connections.
    """

    futures = []
    async for target in gen_dns_records(domain, typ, ipv4, ipv6, xmpps):
        futures.append(asyncio.ensure_future(test_single_socket(target)))
    return [SocketTestResult(t, s) for t, s in await asyncio.gather(*futures)]


def socket_test(domain: str, typ: Check = Check.CLIENT,
                ipv4: bool = True, ipv6: bool = True, xmpps: bool = True) -> tuple:
    """Synchronous wrapper for :py:func:`run_socket_test`."""

    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(run_socket_test(domain, typ, ipv4, ipv6, xmpps))
    tags = tag.pop_all()
    return data, tags
