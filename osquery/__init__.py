"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

__title__ = "osquery"
__version__ = "3.0.6"
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
    "WINDOWS_PLATFORM",
]

from osquery.config_plugin import ConfigPlugin
from osquery.extension_client import DEFAULT_SOCKET_PATH, ExtensionClient, \
    WINDOWS_PLATFORM
from osquery.extension_manager import ExtensionManager
from osquery.logger_plugin import LoggerPlugin
from osquery.management import SpawnInstance, \
    deregister_extension, parse_cli_params, register_plugin, start_extension
from osquery.plugin import BasePlugin
from osquery.singleton import Singleton
from osquery.table_plugin import INTEGER, STRING, TableColumn, TablePlugin
