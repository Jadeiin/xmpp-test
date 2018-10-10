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

import json

from aiohttp import web

from .constants import Check
from .tests.dns import DNSTest
from .tests.socket import SocketTest
from .tests.xmpp import BasicConnectTest
from .tests.xmpp import TLSCipherTest
from .tests.xmpp import TLSVersionTest


_ipv4 = None
_ipv6 = None
_xmpps = None


class JsonApiView(web.View):
    async def post(self):
        print(dir(self))
        request_data = await self.request.read()
        request_data = json.loads(request_data.decode('utf-8'))

        response_data = await self.handle(request_data)
        return web.json_response(response_data)


class TestView(JsonApiView):
    def get_check_type(self, raw_typ):
        return getattr(Check, raw_typ.strip().upper())

    async def handle(self, request_data):
        test_name = self.request.match_info['test']
        domain = request_data['domain']
        typ = self.get_check_type(request_data.get('typ', 'client'))

        print(_ipv4, request_data.get('ipv4', True))
        ipv4 = _ipv4 and request_data.get('ipv4', True)
        ipv6 = _ipv6 and request_data.get('ipv6', True)
        xmpps = _xmpps and request_data.get('xmpps', True)

        if test_name == 'dns':
            test = DNSTest(domain, typ=typ, ipv4=ipv4, ipv6=ipv6, xmpps=xmpps)
        elif test_name == 'socket':
            test = SocketTest(domain, typ=typ, ipv4=ipv4, ipv6=ipv6, xmpps=xmpps)
        elif test_name == 'basic':
            test = BasicConnectTest(domain, typ=typ, ipv4=ipv4, ipv6=ipv6, xmpps=xmpps)
        elif test_name == 'tls_version':
            test = TLSVersionTest(domain, typ=typ, ipv4=ipv4, ipv6=ipv6, xmpps=xmpps)
        elif test_name == 'tls_cipher':
            test = TLSCipherTest(domain, typ=typ, ipv4=ipv4, ipv6=ipv6, xmpps=xmpps)
        else:
            print('Unknown test name: "%s".' % test_name)

        data, tags = await test.aio_start()

        return {
            'data': [d.json() for d in data],
            'tags': [t.as_dict() for t in tags],
        }


def run_server(ipv4: bool = True, ipv6: bool = True, xmpps: bool = True) -> None:
    global _ipv4, _ipv6, _xmpps
    _ipv4 = ipv4
    _ipv6 = ipv6
    _xmpps = xmpps

    app = web.Application()
    app.add_routes([web.post('/test/{test}/', TestView)])

    web.run_app(app)
