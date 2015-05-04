"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

# pylint: disable=too-few-public-methods

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

if __name__ == '__main__':
    unittest.main()
