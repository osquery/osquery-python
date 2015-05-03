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

class MockLoggerPlugin(osquery.LoggerPlugin):
    """Mock logger plugin for testing the logger API"""

    logs = []

    def name(self):
        return "foobar"

    def log_string(self, value):
        self.logs.append(value)

class TestLoggerPlugin(unittest.TestCase):
    """Tests for osquery.LoggerPlugin"""

    def test_simple_call(self):
        """Tests for the call method of osquery.TablePlugin"""
        ext_manager = osquery.ExtensionManager()
        ext_manager.add_plugin(MockLoggerPlugin)
        test_log_string = "test_log_string"
        ext_manager.call("logger",
                         "foobar",
                         {"string":test_log_string})
        mlp = MockLoggerPlugin()
        self.assertTrue(test_log_string in mlp.logs)

if __name__ == '__main__':
    unittest.main()
