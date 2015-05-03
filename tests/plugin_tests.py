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
