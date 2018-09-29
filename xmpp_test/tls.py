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
from typing import List

from .types import TLS_VERSION


def get_supported_protocols(exclude: List[TLS_VERSION] = None) -> List[TLS_VERSION]:
    """Get a list of supported protocols for the current system."""

    if exclude is None:
        exclude = []

    supported = []
    for tls_version in TLS_VERSION:
        if tls_version in exclude:
            continue

        proto = getattr(ssl, 'PROTOCOL_%s' % tls_version.name, None)
        if proto is not None:
            supported.append(tls_version)

    return supported


def get_ciphers(tls_version: TLS_VERSION) -> List[str]:
    ctx = TLS_VERSION.get_context(tls_version)
    return [p['protocol'] for p in ctx.get_ciphers()]
