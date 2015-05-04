"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                "../build/lib/")))

import osquery

class TestBasePlugin(unittest.TestCase):
    """Tests for osquery.Singleton"""

    class SimplePlugin(osquery.BasePlugin):
        """A simple plugin for testing the osquery.BasePlugin class"""

        def call(self, context):
            return None

        def name(self):
            return "pass"

    def test_plugin_inheritance(self):
        """Test that an object derived from BasePlugin works properly"""
        simple_plugin = self.SimplePlugin()
        self.assertEqual(simple_plugin.routes(), [])

if __name__ == '__main__':
    unittest.main()
