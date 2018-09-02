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

import argparse
import json
from .socket import test_client

from tabulate import tabulate


def test():
    parser = argparse.ArgumentParser()
    typ_group = parser.add_mutually_exclusive_group()
    typ_group.add_argument('-c', '--client', dest='typ', action='store_const', const='client',
                           help="Test XMPP client connections (the default).")
    typ_group.add_argument('-s', '--server', dest='typ', action='store_const', const='server',
                           help="Test XMPP server connections.")

    parser.add_argument('-f', '--format', default='table', choices=['table', 'json'],
                        help="Output format to use (default: %(default)s).")

    subparsers = parser.add_subparsers(help='Commands', dest='command')
    test_socket = subparsers.add_parser('test-socket', help='Test socket connections')
    test_socket.add_argument('domain', help="The domain to test.")

    args = parser.parse_args()

    if args.command == 'test-socket':
        results = test_client(args.domain)
        if args.format == 'table':
            results = [(r[0], r[1], 'ok' if r[2] else 'failed') for r in results]
            print(tabulate(results, headers=['IP', 'port', 'status']))
        else:
            data = [{'ip': str(r[0]), 'port': r[1], 'status': r[2]} for r in results]
            print(json.dumps(data))
