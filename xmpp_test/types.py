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

from .constants import STARTTLS_NOT_APPLICABLE
from .constants import STARTTLS_NOT_SUPPORTED
from .constants import STARTTLS_OPTIONAL
from .constants import STARTTLS_REQUIRED
from .constants import STARTTLS_UNKNOWN


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
        return getattr(ssl, 'OP_NO_%s' % tls_version.name)

    def get_context(tls_version: 'TLS_VERSION') -> ssl.SSLContext:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.verify_mode = ssl.CERT_OPTIONAL

        # TODO: without this flag, tests never return
        ctx.check_hostname = False

        # first, disable all protocol versions
        constants = [
            'OP_NO_SSLv2', 'OP_NO_SSLv3', 'OP_NO_TLSv1', 'OP_NO_TLSv1_1', 'OP_NO_TLSv1_2', 'OP_NO_TLSv1_3',
        ]
        for constant in constants:
            if not hasattr(ssl, constant):
                continue

            ctx.options |= getattr(ssl, constant)

        # Reenable the one version we want
        ctx.options &= ~TLS_VERSION.get_protocol_constant(tls_version)
        return ctx


class STARTTLS(Enum):
    """Used for describing STARTTLS support of a connection."""

    unknown: int = STARTTLS_UNKNOWN
    """STARTTLS status is unknown (e.g. if the connection failed)."""

    not_applicable: int = STARTTLS_NOT_APPLICABLE
    """STARTTLS support is not applicable (e.g. XMPPS or websocket connections)."""

    no: int = STARTTLS_NOT_SUPPORTED
    """STARTTLS is not supported."""

    optional: int = STARTTLS_OPTIONAL
    """Supports STARTTLS, but it's not required."""

    required: int = STARTTLS_REQUIRED
    """STARTTLS is required."""
