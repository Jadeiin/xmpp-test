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

from .constants import Check
from .dns import srv_records


def dns_test(domain: str, typ: Check = Check.CLIENT, ipv4: bool = True, ipv6: bool = True) -> dict:
    loop = asyncio.get_event_loop()

    for srv_record in loop.run_until_complete(srv_records('xmpp-client', domain)):
        print(srv_record)

    return {}
