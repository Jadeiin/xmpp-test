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
import csv
import json
import sys

from tabulate import tabulate  # type: ignore

from .constants import Check
from .tests.dns import DNSTest
from .tests.socket import SocketTest
from .tests.xmpp import BasicConnectTest
from .tests.xmpp import TLSCipherTest
from .tests.xmpp import TLSVersionTest


def test() -> None:
    domain_parser = argparse.ArgumentParser(add_help=False)
    domain_parser.add_argument('domain', help="The domain to test.")

    parser = argparse.ArgumentParser()
    typ_group = parser.add_mutually_exclusive_group()
    typ_group.add_argument('-c', '--client', dest='typ', default=Check.CLIENT,
                           action='store_const', const=Check.CLIENT,
                           help="Test XMPP client connections (the default).")
    typ_group.add_argument('-s', '--server', dest='typ', action='store_const', const=Check.SERVER,
                           help="Test XMPP server connections.")

    parser.add_argument('--no-xmpps', dest='xmpps', default=True, action='store_false',
                        help="Do not test XEP-0368 SRV records.")
    parser.add_argument('--no-ipv4', dest='ipv4', default=True, action='store_false',
                        help="Do not test IPv4 connections.")
    parser.add_argument('--no-ipv6', dest='ipv6', default=True, action='store_false',
                        help="Do not test IPv6 connections.")
    parser.add_argument('-f', '--format', default='table', choices=['table', 'json', 'csv'],
                        help="Output format to use (default: %(default)s).")

    subparsers = parser.add_subparsers(help='Commands', dest='command')

    subparsers.add_parser('dns', parents=[domain_parser], help='Test DNS records for this domain.')
    subparsers.add_parser('socket', parents=[domain_parser], help='Simple TCP socket connection test.')
    subparsers.add_parser('basic', parents=[domain_parser], help='Basic XMPP connection test.')
    subparsers.add_parser('tls_version', parents=[domain_parser], help='Test TLS protocol version support.')
    subparsers.add_parser('tls_cipher', parents=[domain_parser], help='Test TLS cipher support.')

    args = parser.parse_args()

    if args.command == 'dns':
        test = DNSTest(args.domain, typ=args.typ, ipv4=args.ipv4, ipv6=args.ipv6, xmpps=args.xmpps)
    elif args.command == 'socket':
        test = SocketTest(args.domain, typ=args.typ, ipv4=args.ipv4, ipv6=args.ipv6, xmpps=args.xmpps)
    elif args.command == 'basic':
        test = BasicConnectTest(args.domain, typ=args.typ, ipv4=args.ipv4, ipv6=args.ipv6, xmpps=args.xmpps)
    elif args.command == 'tls_version':
        test = TLSVersionTest(args.domain, typ=args.typ, ipv4=args.ipv4, ipv6=args.ipv6, xmpps=args.xmpps)
    elif args.command == 'tls_cipher':
        test = TLSCipherTest(args.domain, typ=args.typ, ipv4=args.ipv4, ipv6=args.ipv6, xmpps=args.xmpps)

    data, tags = test.start()

    if args.format == 'table':
        print('###########')
        print('# RESULTS #')
        print('###########')
        print(tabulate([
            d.tabulate() if hasattr(d, 'tabulate') else d.as_dict()
            for d in data
        ], headers='keys'))

        if tags:
            if data:  # we might not have any data to display, and a newline is ugly then
                print('')
            print('########')
            print('# Tags #')
            print('########')
            print(tabulate([t.as_dict() for t in tags], headers='keys'))

    elif args.format == 'csv':
        data = [d.as_dict() for d in data]
        if data:
            writer = csv.DictWriter(sys.stdout, delimiter=',', fieldnames=data[0].keys())
            writer.writeheader()
            for d in data:
                writer.writerow(d)

    elif args.format == 'json':
        print(json.dumps({
            'data': [d.as_dict() for d in data],
            'tags': [t.as_dict() for t in tags],
        }, indent=4))
