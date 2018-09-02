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
from dns import resolver

from .constants import SRV_XMPPS_CLIENT
from .constants import SRV_XMPPS_SERVER
from .constants import SRV_XMPP_CLIENT
from .constants import SRV_XMPP_SERVER


def xmpp_records(domain, ipv4=True, ipv6=True, typ=SRV_XMPPS_CLIENT):
    try:
        srv_records = resolver.query('_%s._tcp.%s' % (typ, domain), 'SRV')
    except (resolver.NXDOMAIN, resolver.NoAnswer):
        return

    for srv_record in srv_records:
        host = srv_record.target.split(1)[0].to_text()

        if ipv4 is True:
            try:
                for record in resolver.query(host, 'A'):
                    yield (host, ipaddress.ip_address(record.address), srv_record.port)
            except (resolver.NXDOMAIN, resolver.NoAnswer):
                pass

        if ipv6 is True:
            try:
                for record in resolver.query(host, 'AAAA'):
                    yield (host, ipaddress.ip_address(record.address), srv_record.port)
            except (resolver.NXDOMAIN, resolver.NoAnswer):
                pass


def xmpp_client_records(domain, ipv4=True, ipv6=True):
    for host, addr, port in xmpp_records(domain, ipv4=ipv4, ipv6=ipv6, typ=SRV_XMPP_CLIENT):
        yield (SRV_XMPP_CLIENT, host, addr, port)
    for host, addr, port in xmpp_records(domain, ipv4=ipv4, ipv6=ipv6, typ=SRV_XMPPS_CLIENT):
        yield (SRV_XMPPS_CLIENT, host, addr, port)


def xmpp_server_records(domain, ipv4=True, ipv6=True):
    for host, addr, port in xmpp_records(domain, ipv4=ipv4, ipv6=ipv6, typ=SRV_XMPP_SERVER):
        yield (SRV_XMPP_SERVER, host, addr, port)
    for host, addr, port in xmpp_records(domain, ipv4=ipv4, ipv6=ipv6, typ=SRV_XMPPS_SERVER):
        yield (SRV_XMPPS_SERVER, host, addr, port)
