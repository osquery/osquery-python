"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import random
import socket
import subprocess
import sys
import tempfile
import threading
import time

# logging support for Python 2.6
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
    logging.NullHandler = NullHandler

from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport import TTransport

from osquery.extensions.ttypes import ExtensionException, InternalExtensionInfo
from osquery.extensions.Extension import Processor
from osquery.extension_client import ExtensionClient, DEFAULT_SOCKET_PATH, WINDOWS_PLATFORM
from osquery.extension_manager import ExtensionManager

if sys.platform == WINDOWS_PLATFORM:
    # We bootleg our own version of Windows pipe coms
    from osquery.TPipe import TPipe
    from osquery.TPipe import TPipeServer

DARWIN_BINARY_PATH = "/usr/local/bin/osqueryd"
LINUX_BINARY_PATH = "/usr/bin/osqueryd"
WINDOWS_BINARY_PATH = "C:\\ProgramData\\osquery\\osqueryd\\osqueryd.exe"


class SpawnInstance(object):
    """Spawn a standalone osquery instance"""
    """The osquery process instance."""
    instance = None
    """The extension client connection attached to the instance."""
    connection = None
    _socket = None

    def __init__(self, path=None):
        """
        Keyword arguments:
        path -- the path to and osqueryd binary to spawn
        """
        if path is None:
            # Darwin is special and must have binaries installed in /usr/local.
            if sys.platform == "darwin":
                self.path = DARWIN_BINARY_PATH
            elif sys.platform == WINDOWS_PLATFORM:
                self.path = WINDOWS_BINARY_PATH
            else:
                self.path = LINUX_BINARY_PATH
        else:
            self.path = path

        # Disable logging for the thrift module (can be loud).
        logging.getLogger('thrift').addHandler(logging.NullHandler())
        if sys.platform == WINDOWS_PLATFORM:
            # Windows fails to spawn if the pidfile already exists
            self._pidfile = (None, tempfile.gettempdir() + '\\pyosqpid-' +
                             str(random.randint(10000, 20000)))
            pipeName = r'\\.\pipe\pyosqsock-' + str(
                random.randint(10000, 20000))
            self._socket = (None, pipeName)
        else:
            self._socket = tempfile.mkstemp(prefix="pyosqsock")

    def __del__(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        if self.instance is not None:
            self.instance.kill()
            self.instance.wait()
            self.instance = None

        # On macOS and Linux mkstemp opens a descriptor.
        if self._socket is not None and self._socket[0] is not None:
            os.close(self._socket[0])
            self._socket = None

    def open(self, timeout=2, interval=0.01):
        """
        Start the instance process and open an extension client

        Keyword arguments:
        timeout -- maximum number of seconds to wait for client
        interval -- seconds between client open attempts
        """
        proc = [
            self.path,
            "--extensions_socket",
            self._socket[1],
            "--disable_database",
            "--disable_watchdog",
            "--disable_logging",
            "--ephemeral",
            "--config_path",
            "/dev/null",
        ]
        self.instance = subprocess.Popen(
            proc,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.connection = ExtensionClient(path=self._socket[1])
        if not self.is_running():
            raise Exception("Cannot start process from path: %s" % (self.path))

        # Attempt to open the extension client.
        delay = 0
        while delay < timeout:
            try:
                self.connection.open()
                return
            except Exception:
                time.sleep(interval)
                delay += interval
        self.instance.kill()
        self.instance = None
        raise Exception("Cannot open connection: %s" % (self._socket[1]))

    def is_running(self):
        """Check if the instance has spawned."""
        if self.instance is None:
            return False
        return self.instance.poll() is None

    @property
    def client(self):
        """The extension client."""
        return self.connection.extension_manager_client()


def parse_cli_params():
    """Parse CLI parameters passed to the extension executable"""
    parser = argparse.ArgumentParser(description=("osquery python extension"))
    parser.add_argument(
        "--socket",
        type=str,
        default=DEFAULT_SOCKET_PATH,
        help="Path to the extensions UNIX domain socket")
    parser.add_argument(
        "--timeout",
        type=int,
        default=1,
        help="Seconds to wait for autoloaded extensions")
    parser.add_argument(
        "--interval",
        type=int,
        default=1,
        help="Seconds delay between connectivity checks")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose informational messages")
    return parser.parse_args()


def start_watcher(client, interval):
    """Ping the osquery extension manager to detect dirty shutdowns."""
    try:
        while True:
            status = client.extension_manager_client().ping()
            if status.code is not 0:
                break
            time.sleep(interval)
    except socket.error:
        # The socket was torn down.
        pass
    os._exit(0)


def start_extension(name="<unknown>",
                    version="0.0.0",
                    sdk_version="1.8.0",
                    min_sdk_version="1.8.0"):
    """Start your extension by communicating with osquery core and starting
    a thrift server.

    Keyword arguments:
    name -- the name of your extension
    version -- the version of your extension
    sdk_version -- the version of the osquery SDK used to build this extension
    min_sdk_version -- the minimum version of the osquery SDK that you can use
    """
    args = parse_cli_params()

    # Disable logging for the thrift module (can be loud).
    logging.getLogger('thrift').addHandler(logging.NullHandler())

    client = ExtensionClient(path=args.socket)

    if not client.open(args.timeout):
        if args.verbose:
            message = "Could not open socket %s" % args.socket
            raise ExtensionException(
                code=1,
                message=message,
            )
        return
    ext_manager = ExtensionManager()

    # try connecting to the desired osquery core extension manager socket
    try:
        status = client.extension_manager_client().registerExtension(
            info=InternalExtensionInfo(
                name=name,
                version=version,
                sdk_version=sdk_version,
                min_sdk_version=min_sdk_version,
            ),
            registry=ext_manager.registry(),
        )
    except socket.error:
        message = "Could not connect to %s" % args.socket
        raise ExtensionException(
            code=1,
            message=message,
        )

    if status.code is not 0:
        raise ExtensionException(
            code=1,
            message=status.message,
        )

    # Start a watchdog thread to monitor the osquery process.
    rt = threading.Thread(target=start_watcher, args=(client, args.interval))
    rt.daemon = True
    rt.start()

    # start a thrift server listening at the path dictated by the uuid returned
    # by the osquery core extension manager
    ext_manager.uuid = status.uuid
    processor = Processor(ext_manager)

    transport = None
    if sys.platform == 'win32':
        transport = TPipeServer(pipe_name="{}.{}".format(args.socket, status.uuid))
    else:
        transport = TSocket.TServerSocket(
            unix_socket=args.socket + "." + str(status.uuid))

    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server.serve()


def deregister_extension():
    """Deregister the entire extension from the core extension manager"""
    args = parse_cli_params()
    client = ExtensionClient(path=args.socket)
    client.open()
    ext_manager = ExtensionManager()

    if ext_manager.uuid is None:
        raise ExtensionException(
            code=1,
            message="Extension Manager does not have a valid UUID",
        )

    try:
        status = client.extension_manager_client().deregisterExtension(
            ext_manager.uuid)
    except socket.error:
        message = "Could not connect to %s" % args.socket
        raise ExtensionException(
            code=1,
            message=message,
        )

    if status.code is not 0:
        raise ExtensionException(
            code=1,
            message=status.message,
        )


def register_plugin(plugin):
    """Decorator wrapper used for registering a plugin class

    To register your plugin, add this decorator to your plugin's implementation
    class:

        @osquery.register_plugin
        class MyTablePlugin(osquery.TablePlugin):
    """
    ext_manager = ExtensionManager()
    ext_manager.add_plugin(plugin)
