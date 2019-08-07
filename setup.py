#!/usr/bin/env python
"""This source code is licensed under the BSD-style license found in the
LICENSE file in the root directory of this source tree. An additional grant
of patent rights can be found in the PATENTS file in the same directory.
"""

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

    _lint_paths = [
        "osquery/*.py",
        "tests/*.py",
    ]

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run the command"""
        system("pylint %s %s" % (
            " ".join(self._pylint_options),
            " ".join(self._lint_paths),
        ))

with open("README.md", "r") as f:
    README = f.read()

with open("osquery/__init__.py", "r") as f:
    __INIT__ = f.read()

TITLE = re.search(r'^__title__\s*=\s*[\'"]([^\'"]*)[\'"]',
                  __INIT__, re.MULTILINE).group(1)
VERSION = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                    __INIT__, re.MULTILINE).group(1)
AUTHOR = re.search(r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]',
                   __INIT__, re.MULTILINE).group(1)
LICENSE = re.search(r'^__license__\s*=\s*[\'"]([^\'"]*)[\'"]',
                    __INIT__, re.MULTILINE).group(1)

setup(name=TITLE,
      version=VERSION,
      description="Osquery Python API",
      long_description=README,
      long_description_content_type="text/markdown",
      author=AUTHOR,
      author_email="osquery@fb.com",
      url="https://osquery.io",
      license=LICENSE,
      packages=[
          "osquery",
          "osquery.extensions",
      ],
      install_requires=[
          "thrift>=0.10",
          "argparse>=1.1",
          "future",
      ],
      test_suite="tests",
      cmdclass={
          "generate": GenerateThriftCommand,
          "lint": LintCommand,
      },
      classifiers=[
          # https://pypi.python.org/pypi?%3Aaction=list_classifiers
          "Development Status :: 5 - Production/Stable",

          "Intended Audience :: System Administrators",
          "Topic :: Security",

          "License :: OSI Approved :: BSD License",

          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.6",
      ],
      keywords="security databases operating systems",)
