"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import dirname, abspath
import json
import sys
import unittest

sys.path.insert(0, abspath("%s/../build/lib" % dirname(abspath(__file__))))

import osquery

class MockConfigPlugin(osquery.ConfigPlugin):
    """Mock config plugin for testing the config API"""

    def name(self):
        return "foobar"

    def content(self):
        return [
            {
                "source_1": json.dumps({
                    "schedule": {
                        "foo": {
                            "query": "select * from foobar",
                            "interval": 5,
                        },
                    },
                }),
            },
        ]

class TestConfigPlugin(unittest.TestCase):
    """Tests for osquery.ConfigPlugin"""

    def test_simple_call(self):
        """Tests for the call method of osquery.TablePlugin"""
        ext_manager = osquery.ExtensionManager()
        ext_manager.add_plugin(MockConfigPlugin)
        response = ext_manager.call("config",
                                    "foobar",
                                    {"action":"genConfig"})
        self.assertEqual(0, response.status.code)
        self.assertTrue(len(response.response) > 0)
        self.assertIn("source_1", response.response[0])

if __name__ == '__main__':
    unittest.main()
