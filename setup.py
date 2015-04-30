#!/usr/bin/env python

from os import system
from setuptools import setup
from setuptools.command.build_py import build_py

class BuildPyCommand(build_py):
    """Override build_py to generate the thrift python code"""

    def run(self):
        build_py.run(self)
        system("thrift -gen py -out build/lib osquery.thrift")

setup(name="osquery",
      version="1.4.4",
      description="osquery python API",
      url="https://osquery.io",
      license="BSD",
      packages=["osquery",],
      install_requires=['thrift>=0.9'],
      test_suite="tests",
      cmdclass={
          "build_py": BuildPyCommand,
      },
)
