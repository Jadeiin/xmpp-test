#!/bin/python

import asyncio
import logging

from slixmpp.stanza import StreamFeatures
from slixmpp.basexmpp import BaseXMPP
from slixmpp.xmlstream.handler import CoroutineCallback
from slixmpp.xmlstream.matcher import MatchXPath

log = logging.getLogger(__name__)


class TestClient(BaseXMPP):
    def __init__(self, *args, **kwargs):
        super(TestClient, self).__init__(*args, **kwargs)
        self.stream_header = "<stream:stream to='%s' %s %s %s %s>" % (
            self.boundjid.host,
            "xmlns:stream='%s'" % self.stream_ns,
            "xmlns='%s'" % self.default_ns,
            "xml:lang='%s'" % self.default_lang,
            "version='1.0'")
        self.stream_footer = "</stream:stream>"

        self.features = set()
        self._stream_feature_handlers = {}
        self._stream_feature_order = []

        self.register_stanza(StreamFeatures)
        self.register_handler(
            CoroutineCallback('Stream Features',
                              MatchXPath('{%s}features' % self.stream_ns),
                              self._handle_stream_features))

        self.register_plugin('feature_starttls')

        self.add_event_handler('stream_negotiated', self.test)

    def test(self, *args, **kwargs):
        self.disconnect()
        return

    @asyncio.coroutine
    def _handle_stream_features(self, features):
        """Process the received stream features.

        :param features: The features stanza.
        """
        for order, name in self._stream_feature_order:
            if name in features['features']:
                handler, restart = self._stream_feature_handlers[name]
                print(name, handler, restart)
                if asyncio.iscoroutinefunction(handler):
                    result = yield from handler(features)
                else:
                    result = handler(features)
                if result and restart:
                    # Don't continue if the feature requires
                    # restarting the XML stream.
                    return True
        log.debug('Finished processing stream features.')
        self.event('stream_negotiated')

    def register_feature(self, name, handler, restart=False, order=5000):
        """Register a stream feature handler.

        :param name: The name of the stream feature.
        :param handler: The function to execute if the feature is received.
        :param restart: Indicates if feature processing should halt with
                        this feature. Defaults to ``False``.
        :param order: The relative ordering in which the feature should
                      be negotiated. Lower values will be attempted
                      earlier when available.
        """
        self._stream_feature_handlers[name] = (handler, restart)
        self._stream_feature_order.append((order, name))
        self._stream_feature_order.sort()


logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')


xmpp = TestClient('user@jabber.at', host='xmpp.jabber.at', port=5222)
xmpp.use_ipv6 = False
xmpp.force_startls = True
xmpp.connect()
xmpp.process(forever=False)

print('#### processed.')
