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


class JsonApiView(web.View):
    async def post(self):
        print(dir(self))
        request_data = await self.request.read()
        request_data = json.loads(request_data.decode('utf-8'))

        response_data = await self.handle(request_data)
        return web.json_response(response_data)


class TestView(JsonApiView):
    async def handle(self, request_data):
        return {'foo': 'bar'}


def run_server():
    app = web.Application()
    app.add_routes([web.post('/test/{name}/', TestView)])

    web.run_app(app)
