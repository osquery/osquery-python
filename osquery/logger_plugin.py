"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

# pylint: disable=no-self-use
# pylint: disable=unused-argument

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from osquery.extensions.ttypes import ExtensionResponse, ExtensionStatus
from osquery.plugin import BasePlugin


class LoggerPlugin(with_metaclass(ABCMeta, BasePlugin)):
    """All logger plugins should inherit from LoggerPlugin"""

    _use_glog_message = "Use Glog for status logging"
    _invalid_action_message = "Not a valid logger plugin action"

    def call(self, context):
        """Internal routing for this plugin type.

        Do not override this method.
        """
        if "string" in context:
            return ExtensionResponse(status=self.log_string(context["string"]),
                                     response=[],)
        elif "snapshot" in context:
            return ExtensionResponse(
                status=self.log_snapshot(context["snapshot"]),
                response=[],)
        elif "health" in context:
            return ExtensionResponse(status=self.log_health(context["health"]),
                                     response=[],)
        elif "init" in context:
            return ExtensionResponse(
                status=ExtensionStatus(code=1,
                                       message=self._use_glog_message,),
                response=[],)
        elif "status" in context:
            return ExtensionResponse(
                status=ExtensionStatus(code=1,
                                       message=self._use_glog_message,),
                response=[],)
        else:
            return ExtensionResponse(
                status=ExtensionStatus(code=1,
                                       message=self._invalid_action_message,),
                response=[],)

    def registry_name(self):
        """The name of the registry type for logger plugins.

        Do not override this method."""
        return "logger"

    @abstractmethod
    def log_string(self, value):
        """The implementation of your logger plugin.

        This must be implemented by your plugin.

        This must return an ExtensionStatus

        Arguments:
        value -- the string to log
        """
        raise NotImplementedError

    def log_health(self, value):
        """If you'd like the log health statistics about osquery's performance,
        override this method in your logger plugin.

        By default, this action is a noop.

        This must return an ExtensionStatus
        """
        return ExtensionStatus(code=0, message="OK",)

    def log_snapshot(self, value):
        """If you'd like to log snapshot queries in a special way, override
        this method.

        By default, this action is just hands off the string to log_string.

        This must return an ExtensionStatus
        """
        return self.log_string(value)
