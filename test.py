import sys
import logging

from xmpp_test import dns
from xmpp_test import clients
from xmpp_test.constants import SRV_XMPPS_CLIENT

logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

for typ, host, addr, port in dns.xmpp_client_records(sys.argv[1]):
    print('#########')
    print(typ, host, addr, port)
    print('#########')

    kwargs = {}
    if typ == SRV_XMPPS_CLIENT:
        kwargs['use_ssl'] = True

    client = clients.TestConnectClient(sys.argv[1], addr, port)
    client.connect(str(addr), port, **kwargs)
    client.process(forever=False)
