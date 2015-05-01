"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

# pylint: disable=too-few-public-methods

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import dirname, abspath
import sys
import unittest

sys.path.insert(0, abspath("%s/../build/lib" % dirname(abspath(__file__))))

import osquery

class TestSingleton(unittest.TestCase):
    """Tests for osquery.Singleton"""

    class MockSingleton(osquery.Singleton):
        """Mock singleton class for testing"""
        pass

    def test_singleton_creation(self):
        """Test that two singletons are the same object"""
        singleton_a = self.MockSingleton()
        singleton_b = self.MockSingleton()
        self.assertEqual(id(singleton_a), id(singleton_b))

@osquery.register_plugin
class MockTablePlugin(osquery.TablePlugin):
    """Mock table plugin for testing the table API"""
    def name(self):
        return "foobar"

    def columns(self):
        return [
            osquery.TableColumn(name="foo", type=osquery.STRING),
            osquery.TableColumn(name="baz", type=osquery.STRING),
        ]

    def generate(self, context):
        query_data = []

        for _ in range(2):
            row = {}
            row["foo"] = "bar"
            row["baz"] = "baz"
            query_data.append(row)

        return query_data

class TestExtensionManager(unittest.TestCase):
    """Tests for osquery.ExtensionManager"""

    def test_plugin_was_registered(self):
        """Tests to ensure that a plugin was registered"""
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

    def test_simple_call(self):
        """Tests for the call method of osquery.TablePlugin"""
        ext_manager = osquery.ExtensionManager()
        results = ext_manager.call("table", "foobar", {"action":"generate"})
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
    unittest.main()
