#!/usr/bin/env python
"""
setup.py
"""

from os import system
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

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run the command"""
        system("pylint osquery/*.py tests/*.py")


with open("README.rst", "r") as f:
    README = f.read()

setup(name="osquery",
      version="1.4.5",
      description="osquery python API",
      long_description=README,
      author="osquery developers",
      author_email="osquery@fb.com",
      url="https://osquery.io",
      license="BSD",
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
