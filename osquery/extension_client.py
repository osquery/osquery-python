"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import time
import sys

from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket
from thrift.transport import TTransport

from osquery.extensions.ExtensionManager import Client

WINDOWS_PLATFORM = "win32"

"""The default path for osqueryd sockets"""
if sys.platform == WINDOWS_PLATFORM:
    # We bootleg our own version of Windows pipe coms
    from osquery.TPipe import TPipe
    DEFAULT_SOCKET_PATH = r'\\.\pipe\osquery.em'
else:
    DEFAULT_SOCKET_PATH = "/var/osquery/osquery.em"

class ExtensionClient(object):
    """A client for connecting to an existing extension manager socket"""

    _protocol = None
    _transport = None

    def __init__(self, path=DEFAULT_SOCKET_PATH, uuid=None):
        """
        Keyword arguments:
        path -- the path of the extension socket to connect to
        uuid -- the additional UUID to use when constructing the socket path
        """
        self.path = path
        sock = None
        if sys.platform == WINDOWS_PLATFORM:
            sock = TPipe(pipe_name=self.path)
        else:
            self.path += ".{}".format(uuid) if uuid else ""
            sock = TSocket.TSocket(unix_socket=self.path)
        self._transport = TTransport.TBufferedTransport(sock)
        self._protocol = TBinaryProtocol.TBinaryProtocol(self._transport)

    def close(self):
        """Close the extension client connection"""
        if self._transport:
            self._transport.close()

    def open(self, timeout=1, interval=0.2):
        """Attempt to open the UNIX domain socket"""
        delay = 0
        while delay < timeout:
            try:
                self._transport.open()
                return True
            except TTransport.TTransportException:
                pass
            delay += interval
            time.sleep(interval)
        return False

    def extension_manager_client(self):
        """Return an extension manager (osquery core) client."""
        return Client(self._protocol)

    def extension_client(self):
        """Return an extension (osquery extension) client."""
        return Client(self._protocol)
