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

import logging
from enum import Enum


class Check(Enum):
    CLIENT: int = 1
    SERVER: int = 0


class SRV_TYPE(Enum):
    XMPP_CLIENT: str = 'xmpp-client'
    XMPP_SERVER: str = 'xmpp-server'
    XMPPS_CLIENT: str = 'xmpps-client'
    XMPPS_SERVER: str = 'xmpps-server'


XMPP_TYPE_PLAIN = 0
XMPP_TYPE_STARTTLS = 1
XMPP_TYPE_TLS = 2

TAG_LEVEL_DEBUG = logging.DEBUG
TAG_LEVEL_INFO = logging.INFO
TAG_LEVEL_WARNING = logging.WARNING
TAG_LEVEL_ERROR = logging.ERROR
