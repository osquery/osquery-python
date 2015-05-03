"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import dirname, abspath
import sys
import unittest

sys.path.insert(0, abspath("%s/../build/lib" % dirname(abspath(__file__))))

import osquery

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

class TestTablePlugin(unittest.TestCase):
    """Tests for osquery.TablePlugin"""

    def test_plugin_was_registered(self):
        """Tests to ensure that a plugin was registered"""
        osquery.ExtensionManager().add_plugin(MockTablePlugin)
        registry = osquery.ExtensionManager().registry()
        self.assertIn("table", registry)
        self.assertIn("foobar", registry["table"])

    def test_routes_are_correct(self):
        """Tests to ensure that a plugins routes are correct"""
        expected = [
            {
                "type": "TEXT",
                "name": "foo",
            },
            {
                "type": "TEXT",
                "name": "baz",
            },
        ]
        osquery.ExtensionManager().add_plugin(MockTablePlugin)
        mtp = MockTablePlugin()
        self.assertEqual(expected, mtp.routes())

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