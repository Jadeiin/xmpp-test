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

import collections
import threading
import typing

from .constants import TAG_TYPE


class Tag(typing.NamedTuple):
    id: int
    level: TAG_TYPE
    message: str
    group: str

    def as_dict(self) -> dict:
        return collections.OrderedDict([
            ('id', self.id),
            ('level', self.level.name),
            ('message', self.message),
            ('group', self.group),
        ])


class Tagger:
    data: threading.local = threading.local()

    def __init__(self) -> None:
        self.data.tags = collections.deque()
        self.data.lock = threading.Lock()

    def append(self, tag: Tag) -> None:
        with self.data.lock:
            self.data.tags.append(tag)

    def debug(self, id: int, message: str, group: str) -> Tag:
        t = Tag(id, TAG_TYPE.DEBUG, message, group)
        self.append(t)
        return t

    def info(self, id: int, message: str, group: str) -> Tag:
        t = Tag(id, TAG_TYPE.INFO, message, group)
        self.append(t)
        return t

    def warning(self, id: int, message: str, group: str) -> Tag:
        t = Tag(id, TAG_TYPE.WARNING, message, group)
        self.append(t)
        return t

    def error(self, id: int, message: str, group: str) -> Tag:
        t = Tag(id, TAG_TYPE.ERROR, message, group)
        self.append(t)
        return t

    def pop_all(self):
        with self.data.lock:
            tags = list(self.data.tags)
            self.data.tags.clear()
        return tags


tag = Tagger()
