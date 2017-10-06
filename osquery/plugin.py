"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

# pylint: disable=no-self-use

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from osquery.singleton import Singleton

class BasePlugin(with_metaclass(ABCMeta, Singleton)):
    """All osquery plugins should inherit from BasePlugin"""

    @abstractmethod
    def call(self, context):
        """Call is the method that is responsible for routing a thrift request
        to the appropriate class method.

        This must be implemented by the plugin type (ie: LoggerPlugin), but
        explicitly not an end-user plugin type (ie: MyAwesomeLoggerPlugin)

        call should return an ExtensionResponse, as defined in osquery.thrift
        """
        raise NotImplementedError

    @abstractmethod
    def name(self):
        """The name of your plugin.

        This must be implemented by your plugin.
        """
        raise NotImplementedError

    def routes(self):
        """The routes that should be broadcasted by your plugin"""
        return []
