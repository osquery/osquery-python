#!/usr/bin/env python

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

setup(name="osquery",
      version="1.4.4",
      description="osquery python API",
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
      },
)
