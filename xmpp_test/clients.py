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

from slixmpp.basexmpp import BaseXMPP
from slixmpp.clientxmpp import ClientXMPP
from slixmpp.stanza import StreamFeatures
from slixmpp.xmlstream.handler import CoroutineCallback
from slixmpp.xmlstream.matcher import MatchXPath

from .constants import SRV_XMPPS_CLIENT
from .dns import xmpp_client_records


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
    pass


def test_client_basic(domain, ipv4=True, ipv6=True):
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    for typ, srv, host, addr, port in xmpp_client_records(domain, ipv4=ipv4, ipv6=ipv6):

        kwargs = {}
        if typ == SRV_XMPPS_CLIENT:
            kwargs['use_ssl'] = True

        client = BasicConnectClient(domain, addr, port)
        client.connect(str(addr), port, **kwargs)
        client.process(forever=False, timeout=10)

        yield typ, addr, port, client._test_success

    client = BasicConnectClient(domain, addr, port + 1)
    client.connect(str(addr), port + 1, **kwargs)
    client.process(forever=False, timeout=10)

    yield typ, addr, port + 1, client._test_success
