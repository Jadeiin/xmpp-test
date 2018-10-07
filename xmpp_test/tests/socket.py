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

        s = socket.socket()
        s.settimeout(2)

        loop = asyncio.get_event_loop()
        try:
            await loop.sock_connect(s, (ip, port))
            return SocketTestResult(target, True)
        except Exception as e:
            return SocketTestResult(target, False)
