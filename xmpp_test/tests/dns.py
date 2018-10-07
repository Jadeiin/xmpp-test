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

"""A set of DNS helper functions."""

from ..base import Test
from ..base import TestResult
from ..base import XMPPTarget
from ..constants import Check


class DNSTestResult(TestResult):
    def __init__(self, target: XMPPTarget, success: bool = True) -> None:
        super().__init__(target, success)

    def as_dict(self) -> dict:
        d = super().as_dict()
        d.pop('success')
        return d

    def tabulate(self) -> dict:
        return self.as_dict()


class DNSTest(Test):
    async def run(self, domain: str, typ: Check = Check.CLIENT,
                  ipv4: bool = True, ipv6: bool = True, xmpps: bool = True) -> tuple:

        records = []
        async for target in XMPPTarget.from_domain(domain, typ, ipv4, ipv6, xmpps):
            records.append(DNSTestResult(target))
        return records
