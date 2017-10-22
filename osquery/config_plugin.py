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

from osquery.extensions.ttypes import ExtensionResponse, ExtensionStatus
from osquery.plugin import BasePlugin

class ConfigPlugin(with_metaclass(ABCMeta, BasePlugin)):
    """All config plugins should inherit from ConfigPlugin"""

    def call(self, context):
        """Internal routing for this plugin type.

        Do not override this method.
        """
        if "action" in context:
            if context["action"] == "genConfig":
                return ExtensionResponse(status=ExtensionStatus(code=0,
                                                                message="OK",),
                                         response=self.content(),)

        message = "Not a valid config plugin action"
        return ExtensionResponse(status=ExtensionStatus(code=1,
                                                        message=message,),
                                 response=[],)

    def registry_name(self):
        """The name of the registry type for config plugins.

        Do not override this method.
        """
        return "config"

    @abstractmethod
    def content(self):
        """The implementation of your config plugin.

        This should return a dictionary of the following format:

            [
                {
                    "source_name_1": serialized_json_config_string_1,
                    "source_name_2": serialized_json_config_string_2,
                }
            ]

        Consider the following full example of the content method:

            @osquery.register_plugin
            class TestConfigPlugin(osquery.ConfigPlugin):
                def name(self):
                    return "test_config"

                def content(self):
                    return [
                        {
                            "source_one": json.dumps({
                                "schedule": {
                                    "time_1": {
                                        "query": "select * from time",
                                        "interval": 1,
                                    },
                                },
                            }),
                            "source_two": json.dumps({
                                "schedule": {
                                    "time_2": {
                                        "query": "select * from time",
                                        "interval": 2,
                                    },
                                },
                            }),
                        }
                    ]

        This must be implemented by your plugin.
        """
        raise NotImplementedError
