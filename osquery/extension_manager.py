"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import threading
import time

from osquery.extensions.Extension import Iface
from osquery.extensions.ttypes import ExtensionResponse, ExtensionStatus
from osquery.singleton import Singleton

def shutdown_request(code, timeout=1):
    """A delayed shutdown request."""
    time.sleep(timeout)
    os._exit(code)

class ExtensionManager(Singleton, Iface):
    """The thrift server for handling extension requests

    An extension's manager is responsible for maintaining the state of
    registered plugins, broadcasting the registry of those plugins to the
    core's extension manager and fielding requests that come in on the
    extension's socket.
    """
    _plugins = {}
    _registry = {}

    uuid = None

    def add_plugin(self, plugin):
        """Register a plugin with the extension manager. In order for the
        extension manager to broadcast a plugin, it must be added using this
        interface.

        Keyword arguments:
        plugin -- the plugin class to register
        """

        # First, we create an instance of the plugin. All plugins are
        # singletons, so this instance will be long-lived.
        obj = plugin()


        # When the extension manager broadcasts it's registry to core's
        # extension manager, the data structure should follow a specific
        # format. Whenever we add a plugin, we need to update the internal
        # _registry instance variable, which will be sent to core's extension
        # manager once the extension has been started
        if obj.registry_name() not in self._registry:
            self._registry[obj.registry_name()] = {}
        if obj.name() not in self._registry[obj.registry_name()]:
            self._registry[obj.registry_name()][obj.name()] = obj.routes()

        # The extension manager needs a way to route calls to the appropriate
        # implementation class. We maintain references to the plugin's
        # singleton instantiation in the _plugins instance variable. The
        # _plugins member has the same general structure as _registry, but
        # instead of pointing to the plugin's routes, it points to the plugin
        # implementation object
        if obj.registry_name() not in self._plugins:
            self._plugins[obj.registry_name()] = {}
        if obj.name() not in self._plugins[obj.registry_name()]:
            self._plugins[obj.registry_name()][obj.name()] = obj

    def shutdown(self):
        """The osquery extension manager requested a shutdown"""
        rt = threading.Thread(target=shutdown_request, args=(0,))
        rt.daemon = True
        rt.start()
        return ExtensionStatus(code=0, message="OK")

    def registry(self):
        """Accessor for the internal _registry member variable"""
        return self._registry

    def ping(self):
        """Lightweight health verification

        The core osquery extension manager will periodically "ping" each
        extension that has connected to it to ensure that the extension is
        still active and can field requests, if necessary.
        """
        return ExtensionStatus(code=0, message="OK")

    def call(self, registry, item, request):
        """The entry-point for plugin requests

        When a plugin is accessed from another process, osquery core's
        extension manager will send a thrift request to the implementing
        extension manager's call method.

        Arguments:
        registry -- a string representing what registry is being accessed.
            for config plugins this is "config", for table plugins this is
            "table", etc.
        item -- the registry item that is being requested. this is the "name"
            of your plugin. for example, this would be the exact name of the
            SQL table, if the plugin was a table plugin.
        """

        # this API only support plugins of the following types:
        # - table
        # - config
        # - logger
        if registry not in ["table", "config", "logger"]:
            message = "A registry of an unknown type was called: %s" % registry
            return ExtensionResponse(
                status=ExtensionStatus(code=1, message=message,),
                response=[],)

        try:
            return self._plugins[registry][item].call(request)
        except KeyError:
            message = "Extension registry does not contain requested plugin"
            return ExtensionResponse(
                status=ExtensionStatus(code=1, message=message,),
                response=[],)
