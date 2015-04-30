#  LICENSE file in the root directory of this source tree. An additional grant
#  of patent rights can be found in the PATENTS file in the same directory.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import errno
from os.path import dirname, abspath
import os
import random
import shutil
import string
import sys
import time
import threading
import unittest

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

sys.path.insert(0, abspath("%s/../build/lib" % dirname(abspath(__file__))))

import osquery

def generate_uuid():
    return "".join(random.choice(string.ascii_uppercase + string.digits) \
    for _ in range(10))

TEST_SOCKET_PATH = "/tmp/osquery-testing/python_ext_%s.em" % generate_uuid()

class MockOsqueryExtensionManager(osquery.extensions.Extension.Iface):
    """This is a mock osquery core extension manager. It pretends to be
    osqueryd's extension socket and responds to thrift calls appropriately
    """

    def registerExtension(info, registry):
        return osquery.extensions.ttypes.ExtensionStatus(code=0,
                                                         message="OK",
                                                         uuid=generate_uuid(),)

    def deregisterExtension(uuid):
        return osquery.extensions.ttypes.ExtensionStatus(code=0, message="OK")

    def query(sql):
        return self.call(None, None, None)

    def call(registry, item, request):
        return osquery.extensions.ttypes.ExtensionResponse(
            status=osquery.extensions.ttypes.ExtensionStatus(code=0,
                                                             message="OK",),
            response=[
                {
                    "foo": "bar",
                    "baz": "baz",
                },
                {
                    "foo": "bar",
                    "baz": "baz",
                },
                {
                    "foo": "bar",
                    "baz": "baz",
                },
            ],
        )
        pass

    def ping():
        return osquery.extensions.ttypes.ExtensionStatus(code=0, message="OK")

def create_mock_server():
    handler = MockOsqueryExtensionManager()
    processor = osquery.extensions.Extension.Processor(handler)
    transport = transport = TSocket.TServerSocket(unix_socket=TEST_SOCKET_PATH)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server_thread = threading.Thread(target=server.serve)
    server_thread.daemon = True
    server_thread.start()

class TestSingleton(unittest.TestCase):

    class MockSingleton(osquery.Singleton):
        pass

    def test_singleton_creation(self):
        a = self.MockSingleton()
        b = self.MockSingleton()
        self.assertEqual(id(a), id(b))

class TestExtensionClient(unittest.TestCase):

    def test_create_client(self):
        try:
            client = osquery.ExtensionClient(path=TEST_SOCKET_PATH)
            client.open()
        except Exception as e:
            self.fail("Could not connect to manager socket: %s" % e)
        client.close()

@osquery.register_plugin
class MockTablePlugin(osquery.TablePlugin):
    def name(self):
        return "foobar"

    def columns(self):
        return [
            osquery.TableColumn(name="foo", type=osquery.STRING),
            osquery.TableColumn(name="baz", type=osquery.STRING),
        ]

    def generate(self, context):
        query_data = []

        for i in range(2):
            row = {}
            row["foo"] = "bar"
            row["baz"] = "baz"
            query_data.append(row)

        return query_data

class TestExtensionManager(unittest.TestCase):

    def test_plugin_was_registered(self):
        registry = {
            "table": {
                "foobar": [
                    {
                        "type": "TEXT",
                        "name": "foo",
                    },
                    {
                        "type": "TEXT",
                        "name": "baz",
                    },
                ],
            },
        }
        self.assertEqual(osquery.ExtensionManager().registry(), registry)

    def test_call(self):
        results = osquery.ExtensionManager().call("table", "foobar", None)
        expected = [
            {
                "foo": "bar",
                "baz": "baz",
            },
            {
                "foo": "bar",
                "baz": "baz",
            },
        ]
        self.assertEqual(results.response, expected)

if __name__ == '__main__':
    try:
        os.mkdir("/tmp/osquery-testing")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
    create_mock_server()
    time.sleep(1)
    unittest.main(exit=False)
    shutil.rmtree("/tmp/osquery-testing/")
