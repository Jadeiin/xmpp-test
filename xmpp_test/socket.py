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

import ipaddress
import socket
#from .dns import xmpp_client_records
#from .dns import xmpp_server_records


def test_socket(address, port):
    """Test a host/port pair by creating a basic socket connection.

    This does no more then simply open a socket to see if that succeeds. This will happily return ``True`` no
    matter the server listening on that port or if TLS connection would be required to connect to it or not.
    """
    if isinstance(address, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
        address = str(address)

    try:
        with socket.create_connection((address, port), timeout=2):
            pass
    except Exception as e:
        return False

    return True


def test_client(domain, ipv4=True, ipv6=True):
    """Test all XMPP client records."""

    for typ, srv, host, addr, port in xmpp_client_records(domain, ipv4=ipv4, ipv6=ipv6):
        yield (typ, srv, host, addr, port, test_socket(addr, port))


def test_server(domain, ipv4=True, ipv6=True):
    """Test all XMPP server records."""

    for typ, srv, host, addr, port in xmpp_server_records(domain, ipv4=ipv4, ipv6=ipv6):
        yield (typ, srv, host, addr, port, test_socket(addr, port))
