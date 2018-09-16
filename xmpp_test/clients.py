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
from typing import Tuple

from slixmpp.basexmpp import BaseXMPP  # type: ignore
from slixmpp.clientxmpp import ClientXMPP  # type: ignore
from slixmpp.stanza import StreamFeatures  # type: ignore
from slixmpp.xmlstream.handler import CoroutineCallback  # type: ignore
from slixmpp.xmlstream.matcher import MatchXPath  # type: ignore

from .constants import Check
from .tags import tag
from .dns import gen_dns_records
from .dns import XMPPTarget


class ConnectClientBase(BaseXMPP):
    def __init__(self, host, address, port, *args, **kwargs):
        self._test_host = host
        self._test_address = address
        self._test_port = port
        self._test_success = False

        super().__init__(*args, **kwargs)
        self.stream_header = "<stream:stream to='%s' %s %s %s %s>" % (
            host,
            "xmlns:stream='%s'" % self.stream_ns,
            "xmlns='%s'" % self.default_ns,
            "xml:lang='%s'" % self.default_lang,
            "version='1.0'")
        self.stream_footer = "</stream:stream>"

        self.features = set()
        self._stream_feature_handlers = {}
        self._stream_feature_order = []

        self.register_stanza(StreamFeatures)
        self.register_handler(
            CoroutineCallback('Stream Features',
                              MatchXPath('{%s}features' % self.stream_ns),
                              self._handle_stream_features))

        self.register_plugin('feature_starttls')

        self.add_event_handler('stream_negotiated', self.handle_stream_negotiated)
        self.add_event_handler('session_end', self.handle_stream_end)
        self.add_event_handler('connection_failed', self.handle_connection_failed)

    _handle_stream_features = ClientXMPP._handle_stream_features
    register_feature = ClientXMPP.register_feature

    async def pick_dns_answer(self, default_domain):
        return self._test_host, str(self._test_address), self._test_port

    def handle_stream_negotiated(self, *args, **kwargs):
        print('stream negotiated:', args, kwargs)
        self._test_success = True
        self.abort()

    def handle_stream_end(self, *args, **kwargs):
        print('session end:', args, kwargs)
        self.abort()

    def handle_connection_failed(self, exception):
        print('connection failed', exception)
        self.abort()
        if not self.disconnected.cancelled():
            self.disconnected.set_result(True)
            self.disconnected = asyncio.Future()


class BasicConnectClient(ConnectClientBase):
    async def process(self, *, forever=True, timeout=None):
        tasks = [asyncio.sleep(timeout)]
        if not forever:
            tasks.append(self.disconnected)
        await asyncio.ensure_future(asyncio.wait(tasks))


class BasicConnectTestResult:
    target: XMPPTarget
    success: bool

    def __init__(self, target: XMPPTarget, success: bool) -> None:
        self.target = target
        self.success = success

    def as_dict(self) -> dict:
        d = self.target.as_dict()
        d['status'] = self.success
        return d

    def tabulate(self) -> dict:
        d = self.as_dict()
        d['status'] = 'working' if d['status'] else 'failed'
        return d


async def test_basic_target(domain: str, target: XMPPTarget) -> Tuple[XMPPTarget, bool]:
    ip = str(target.ip)
    port = target.srv.port

    kwargs = {
        'use_ssl': target.is_xmpps,
    }
    client = BasicConnectClient(domain, ip, port)
    client.connect(ip, port, **kwargs)
    await client.process(forever=False, timeout=10)

    return target, client._test_success


async def run_basic_client_test(domain: str, typ: Check = Check.CLIENT,
                                ipv4: bool = True, ipv6: bool = True, xmpps: bool = True) -> tuple:

    futures = []
    async for target in gen_dns_records(domain, typ, ipv4, ipv6, xmpps):
        futures.append(asyncio.ensure_future(test_basic_target(domain, target)))
    return [BasicConnectTestResult(t, s) for t, s in await asyncio.gather(*futures)]


def basic_client_test(domain: str, typ: Check = Check.CLIENT,
                      ipv4: bool = True, ipv6: bool = True, xmpps: bool = True) -> tuple:

    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(run_basic_client_test(domain, typ, ipv4, ipv6, xmpps))
    tags = tag.pop_all()
    return data, tags
