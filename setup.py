#!/usr/bin/env python
"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""""

from os import system
import re
from setuptools import setup, Command

class GenerateThriftCommand(Command):
    """Generate thrift code"""

    description = "Generate thrift code"
    user_options = []

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run the command"""
        system("thrift -gen py -out . osquery.thrift")
        system("rm osquery/extensions/*-remote")
        system("rm __init__.py")

class LintCommand(Command):
    """Run pylint on implementation and test code"""

    description = "Run pylint on implementation and test code"
    user_options = []

    _pylint_options = [
        "--max-line-length 80",
        "--ignore-imports yes"
    ]

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run the command"""
        system("pylint %s osquery/*.py tests/*.py" % " ".join(
            self._pylint_options))

with open("README.rst", "r") as f:
    README = f.read()

with open("osquery/__init__.py", "r") as f:
    __INIT__ = f.read()

TITLE = re.search(r'^__title__\s*=\s*[\'"]([^\'"]*)[\'"]',
                  __INIT__, re.MULTILINE).group(1)
VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                    __INIT__, re.MULTILINE).group(1)
DESCRIPTION = re.search(r'^__description__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        __INIT__, re.MULTILINE).group(1)
AUTHOR = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]',
                   __INIT__, re.MULTILINE).group(1)
AUTHOR_EMAIL = re.search(r'^__author_email__\s*=\s*[\'"]([^\'"]*)[\'"]',
                         __INIT__, re.MULTILINE).group(1)
URL = re.search(r'^__url__\s*=\s*[\'"]([^\'"]*)[\'"]',
                __INIT__, re.MULTILINE).group(1)
LICENSE = re.search(r'^__license__\s*=\s*[\'"]([^\'"]*)[\'"]',
                    __INIT__, re.MULTILINE).group(1)

setup(name=TITLE,
      version=VERSION,
      description=DESCRIPTION,
      long_description=README,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      url=URL,
      license=LICENSE,
      packages=["osquery",],
      install_requires=[
          'thrift>=0.9',
          'argparse>=1.1',
      ],
      test_suite="tests",
      cmdclass={
          "generate": GenerateThriftCommand,
          "lint": LintCommand,
      },)
