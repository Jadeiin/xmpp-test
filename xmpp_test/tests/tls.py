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

from ..base import Test
from ..tls import get_protocol_ciphers
from ..tls import get_supported_protocols


class TLSVersionResult:
    def __init__(self, version):
        self.version = version

    def as_dict(self) -> dict:
        return {'version': self.version.name}

    def json(self) -> dict:
        return self.as_dict()


class TLSCipherResult:
    def __init__(self, version, cipher):
        self.version = version
        self.cipher = cipher

    def as_dict(self) -> dict:
        return {'version': self.version.name, 'cipher': self.cipher}

    def json(self) -> dict:
        return self.as_dict()


class TLSSupportedTest(Test):
    async def run(self, what):
        if what == 'version':
            return [TLSVersionResult(v) for v in get_supported_protocols()]

        elif what == 'cipher':
            ciphers = []
            async for tls_version, cipher in get_protocol_ciphers():
                ciphers.append(TLSCipherResult(tls_version, cipher))

            return ciphers
