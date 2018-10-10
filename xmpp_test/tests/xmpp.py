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

import ssl

from ..base import TestResult
from ..base import XMPPTarget
from ..base import XMPPTargetTest
from ..clients import BasicConnectClient
from ..clients import TLSTestClient
from ..tls import get_protocol_ciphers
from ..tls import get_supported_protocols
from ..types import TLS_VERSION
from ..types import STARTTLS


class BasicConnectTestResult(TestResult):
    starttls_required: STARTTLS

    def __init__(self, target: XMPPTarget, success: bool, starttls_required: STARTTLS) -> None:
        super().__init__(target, success)
        self.starttls_required = starttls_required

    def as_dict(self) -> dict:
        d = super().as_dict()
        d['starttls'] = self.starttls_required
        return d

    def tabulate(self) -> dict:
        d = super().tabulate()
        d['starttls'] = d['starttls'].name
        return d

    def json(self) -> dict:
        d = super().json()
        d['starttls'] = d['starttls'].value
        return d


class BasicConnectTest(XMPPTargetTest):
    async def target_test(self, target: XMPPTarget) -> BasicConnectTestResult:
        ip = str(target.ip)
        port = target.srv.port

        kwargs = {
            'use_ssl': target.is_xmpps,
        }
        client = BasicConnectClient(target.srv.domain, ip, port)
        client.connect(ip, port, **kwargs)
        await client.process(forever=False, timeout=10)

        return BasicConnectTestResult(target, client._test_success, client.starttls_required)


class TLSVersionTestResult(BasicConnectTestResult):
    context: ssl.SSLContext
    tls_version: TLS_VERSION

    def __init__(self, target: XMPPTarget, success: bool,
                 starttls_required: STARTTLS, context: ssl.SSLContext, tls_version: TLS_VERSION) -> None:
        super().__init__(target, success, starttls_required=starttls_required)
        self.context = context
        self.tls_version = tls_version

    def as_dict(self) -> dict:
        d = super().as_dict()
        d['protocol'] = self.tls_version.name
        return d


class TLSVersionTest(XMPPTargetTest):
    async def get_tests(self, domain, target):
        for tls_version in get_supported_protocols():
            yield {'tls_version': tls_version}

    async def target_test(self, target: XMPPTarget, tls_version: TLS_VERSION) -> TLSVersionTestResult:
        ip = str(target.ip)
        port = target.srv.port

        kwargs = {
            'use_ssl': target.is_xmpps,
        }
        context = TLS_VERSION.get_context(tls_version)
        client = TLSTestClient(context, target.srv.domain, ip, port)
        client.connect(ip, port, **kwargs)
        await client.process(forever=False, timeout=10)

        return TLSVersionTestResult(target, client._test_success, context=context, tls_version=tls_version,
                                    starttls_required=client.starttls_required)


class TLSCipherTestResult(TLSVersionTestResult):
    def __init__(self, *args, cipher: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.cipher = cipher

    def as_dict(self) -> dict:
        d = super().as_dict()
        d['cipher'] = self.cipher
        return d


class TLSCipherTest(XMPPTargetTest):
    async def get_tests(self, domain, target):
        async for tls_version, cipher in get_protocol_ciphers():
            yield {'tls_version': tls_version, 'cipher': cipher}

    async def target_test(self, target: XMPPTarget, tls_version: TLS_VERSION,
                          cipher: str) -> TLSVersionTestResult:
        ip = str(target.ip)
        port = target.srv.port

        kwargs = {
            'use_ssl': target.is_xmpps,
        }

        context = TLS_VERSION.get_context(tls_version)
        context.set_ciphers(cipher)

        client = TLSTestClient(context, target.srv.domain, ip, port)
        client.connect(ip, port, **kwargs)
        await client.process(forever=False, timeout=10)

        return TLSCipherTestResult(target, client._test_success, context=context,
                                   tls_version=tls_version, cipher=cipher,
                                   starttls_required=client.starttls_required)
