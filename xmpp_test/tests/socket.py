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
import ipaddress

from ..base import TestResult
from ..base import XMPPTarget
from ..base import XMPPTargetTest


class SocketTestResult(TestResult):
    """A test result for a socket test."""

    pass


class SocketTest(XMPPTargetTest):
    async def target_test(self, target: XMPPTarget) -> SocketTestResult:
        ip = str(target.ip)
        port = target.srv.port

        # Determine address family based on IP version
        try:
            addr = ipaddress.ip_address(ip)
            family = socket.AF_INET6 if addr.version == 6 else socket.AF_INET
        except ValueError:
            return SocketTestResult(target, False)

        # Create appropriate socket type
        s = socket.socket(family=family, type=socket.SOCK_STREAM)
        s.setblocking(False)  # Required for async operations

        loop = asyncio.get_event_loop()
        try:
            # Use async timeout handling
            await asyncio.wait_for(loop.sock_connect(s, (ip, port)), timeout=2)
            return SocketTestResult(target, True)
        except (OSError, asyncio.TimeoutError):
            return SocketTestResult(target, False)
        finally:
            s.close()  # Ensure socket is closed
