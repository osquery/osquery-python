"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

__title__ = "osquery"
__version__ = "2.3.0"
__author__ = "osquery developers"
__license__ = "BSD"
__copyright__ = "Copyright 2015 Facebook"
__url__ = "https://osquery.io"

__all__ = [
    "BasePlugin",
    "ConfigPlugin",
    "DEFAULT_SOCKET_PATH",
    "deregister_extension",
    "ExtensionClient",
    "ExtensionManager",
    "INTEGER",
    "LoggerPlugin",
    "parse_cli_params",
    "register_plugin",
    "start_extension",
    "Singleton",
    "SpawnInstance",
    "STRING",
    "TableColumn",
    "TablePlugin",
]

try:
    from thrift.util import Recursive

    # If this succeeds then we are using fbthrift.
    # 'Monkeypatch' the extensions module to use fbthrift-generated code.
    import sys
    import importlib
    if 'osquery.extensions' in sys.modules:
        del sys.modules['osquery.extensions']

    try:
        sys.modules['osquery.extensions'] = importlib.import_module(
            'osquery.extensions.fbthrift')
    except ImportError:
        # The local fbthrift-generated code is not available.
        pass
except ImportError:
    # We are using Apache thrift.
    pass

from osquery.config_plugin import ConfigPlugin
from osquery.extension_client import DEFAULT_SOCKET_PATH, ExtensionClient
from osquery.extension_manager import ExtensionManager
from osquery.logger_plugin import LoggerPlugin
from osquery.management import SpawnInstance, \
    deregister_extension, parse_cli_params, register_plugin, start_extension
from osquery.plugin import BasePlugin
from osquery.singleton import Singleton
from osquery.table_plugin import INTEGER, STRING, TableColumn, TablePlugin
