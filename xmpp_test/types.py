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
from enum import Enum


class TLS_VERSION(Enum):
    """Enum for different TLS versions.

    The values here match constants from the ``ssl`` module but are duplicated here because constants in the
    module are not always present.

    >>> ssl.PROTOCL_TLSv1.value == TLS_VERSION.TLSv1.value
    True
    """

    SSLv2: int = 1
    SSLv3: int = 2
    TLSv1: int = 3
    TLSv1_1: int = 4
    TLSv1_2: int = 5
    TLSv1_3: int = 6

    def get_protocol_constant(tls_version: 'TLS_VERSION') -> ssl._SSLMethod:
        return getattr(ssl, 'PROTOCOL_%s' % tls_version.name)

    def get_context(tls_version: 'TLS_VERSION') -> ssl.SSLContext:
        return ssl.SSLContext(TLS_VERSION.get_protocol_constant(tls_version))
