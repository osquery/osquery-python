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
from builtins import str
from collections import namedtuple
from future.utils import with_metaclass
import json
import logging

from osquery.extensions.ttypes import ExtensionResponse, ExtensionStatus
from osquery.plugin import BasePlugin

class TablePlugin(with_metaclass(ABCMeta, BasePlugin)):
    """All table plugins should inherit from TablePlugin"""

    _no_action_message = "Table plugins must include a request action"

    def call(self, context):
        """Internal routing for this plugin type.

        Do not override this method.
        """
        if "action" not in context:
            return ExtensionResponse(
                status=ExtensionStatus(code=1,
                                       message=self._no_action_message,),
                response=[],)

        if context["action"] == "generate":
            ctx = {}
            if "context" in context:
                ctx = json.dumps(context["context"])
            rows = self.generate(ctx)
            for i, row in enumerate(rows):
                for key, value in row.items():
                    if not isinstance(value, str):
                        try:
                            rows[i][key] = str(value)
                        except ValueError as e:
                            rows[i][key] = ''
                            logging.error("Cannot convert key %s: %s" % (
                                i, key, str(e)))
            return ExtensionResponse(
                status=ExtensionStatus(code=0, message="OK",),
                response=rows)
        elif context["action"] == "columns":
            return ExtensionResponse(
                status=ExtensionStatus(code=0, message="OK",),
                response=self.routes(),)
        return ExtensionResponse(code=1, message="Unknown action",)

    def registry_name(self):
        """The name of the registry type for table plugins.

        Do not override this method."""
        return "table"

    def routes(self):
        """The routes that will be broadcasted for table plugins

        Do not override this method.
        """
        routes = []
        for column in self.columns():
            route = {
                "id": "column",
                "name": column.name,
                "type": column.type,
                "op": "0",
            }
            routes.append(route)
        return routes

    @abstractmethod
    def columns(self):
        """The columns of your table plugin.

        This method should return an array of osquery.TableColumn instances.

        Consider the following example:

            class MyTablePlugin(osquery.TablePlugin):
                def columns(self):
                    return [
                        osquery.TableColumn(name="foo", type=osquery.STRING),
                        osquery.TableColumn(name="baz", type=osquery.STRING),
                    ]

        This must be implemented by your plugin.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, context):
        """The implementation of your table plugin.

        This method should return a list of dictionaries, such that each
        dictionary has a key corresponding to each of your table's columns.

        Consider the following example:

            class MyTablePlugin(osquery.TablePlugin):
                def generate(self, context):
                    query_data = []

                    for i in range(5):
                        row = {}
                        row["foo"] = "bar"
                        row["baz"] = "boo"
                        query_data.append(row)

                    return query_data

        This must be implemented by your plugin.
        """
        raise NotImplementedError

STRING = "TEXT"
"""The text SQL column type"""

INTEGER = "INTEGER"
"""The integer SQL column type"""

TableColumn = namedtuple("TableColumn", ["name", "type"])
"""An object which allows you to define the name and type of a SQL column"""
