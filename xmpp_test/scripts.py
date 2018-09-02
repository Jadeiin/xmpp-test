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

from tabulate import tabulate

from .clients import test_client_basic
from .socket import test_client
from .socket import test_server


def test():
    parser = argparse.ArgumentParser()
    typ_group = parser.add_mutually_exclusive_group()
    typ_group.add_argument('-c', '--client', dest='typ', default='client',
                           action='store_const', const='client',
                           help="Test XMPP client connections (the default).")
    typ_group.add_argument('-s', '--server', dest='typ', action='store_const', const='server',
                           help="Test XMPP server connections.")

    parser.add_argument('--no-ipv4', dest='ipv4', default=True, action='store_false',
                        help="Do not test IPv4 connections.")
    parser.add_argument('--no-ipv6', dest='ipv6', default=True, action='store_false',
                        help="Do not test IPv6 connections.")
    parser.add_argument('-f', '--format', default='table', choices=['table', 'json', 'csv'],
                        help="Output format to use (default: %(default)s).")

    subparsers = parser.add_subparsers(help='Commands', dest='command')
    test_socket = subparsers.add_parser(
        'socket', help='Test a domain by doing a simple socket connection to each DNS entry.')
    test_socket.add_argument('domain', help="The domain to test.")

    test_socket = subparsers.add_parser(
        'basic', help='Basic XMPP connection test.')
    test_socket.add_argument('domain', help="The domain to test.")

    args = parser.parse_args()

    if args.command == 'socket':
        if args.typ == 'client':
            results = test_client(args.domain, ipv4=args.ipv4, ipv6=args.ipv6)
        elif args.typ == 'server':
            results = test_server(args.domain, ipv4=args.ipv4, ipv6=args.ipv6)

        fieldnames = ['SRV', 'A/AAAA', 'IP', 'port', 'status']
        if args.format == 'table':
            results = [(r[1], r[2], r[3], r[4], 'ok' if r[5] else 'failed') for r in results]
            print(tabulate(results, headers=fieldnames))
        elif args.format == 'csv':
            writer = csv.writer(sys.stdout, delimiter=',')
            writer.writerow(fieldnames)
            for r in results:
                writer.writerow((r[1], r[2], r[3], r[4], 'ok' if r[5] else 'failed'))
        else:
            data = [{
                'srv': r[1],
                'host': r[2],
                'ip': str(r[3]),
                'port': r[4],
                'status': r[5]
            } for r in results]
            print(json.dumps(data))

    elif args.command == 'basic':
        results = test_client_basic(args.domain, ipv4=args.ipv4, ipv6=args.ipv6)
        print(list(results))
