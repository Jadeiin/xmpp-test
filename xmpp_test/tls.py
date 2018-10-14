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

import asyncio
import ssl
import sys
from typing import List

from .types import TLS_VERSION


# if the ssl module has the HAS_* constants - added in Python 3.7.
_SSL_HAS_HAS_CONSTANTS = sys.version_info[:2] >= (3, 7)


def get_supported_protocols(exclude: List[TLS_VERSION] = None) -> List[TLS_VERSION]:
    """Get a list of supported protocols for the current system."""

    if exclude is None:
        exclude = []

    supported = []
    for tls_version in reversed(TLS_VERSION):
        if tls_version in exclude:
            continue

        if _SSL_HAS_HAS_CONSTANTS:
            # Python 3.7 no longer has all PROTOCOL_* constants
            if getattr(ssl, 'HAS_%s' % tls_version.name, False):
                supported.append(tls_version)
        else:
            proto = getattr(ssl, 'PROTOCOL_%s' % tls_version.name, None)
            if proto is not None:
                supported.append(tls_version)

    return supported


async def get_ciphers(tls_version: TLS_VERSION) -> List[str]:
    ctx = TLS_VERSION.get_context(tls_version)
    if hasattr(ctx, 'get_ciphers') and False:
        ciphers = [p['name'] for p in ctx.get_ciphers()]
    else:
        create = asyncio.create_subprocess_exec('openssl', 'ciphers', 'ALL:!aNULL:!SRP:!PSK',
                                                stdout=asyncio.subprocess.PIPE)
        proc = await create
        ciphers = await proc.stdout.read()
        ciphers = ciphers.strip().decode('utf-8').split(':')

    for c in ciphers:
        yield c


async def get_protocol_ciphers():
    duplicates = set()

    for tls_version in get_supported_protocols():
        async for cipher in get_ciphers(tls_version):
            if cipher in duplicates:
                continue
            duplicates.add(cipher)

            yield tls_version, cipher
