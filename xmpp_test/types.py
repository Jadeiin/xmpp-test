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

from enum import Enum


class TLS_VERSION(Enum):
    """Enum for different TLS versions."""

    SSL_2: int = 0
    SSL_3: int = 1
    TLS_1_0: int = 2
    TLS_1_1: int = 3
    TLS_1_2: int = 4
    TLS_1_3: int = 5
