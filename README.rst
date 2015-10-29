osquery-python
==============

.. image:: https://i.imgur.com/9Vy2GFx.png
  :target: https://osquery.io

`osquery <https://github.com/facebook/osquery>`_ exposes an operating system as
a high-performance relational database. This allows you to write SQL-based
queries to explore operating system data. With osquery, SQL tables represent
abstract concepts such as running processes, loaded kernel modules, open
network connections, browser plugins, hardware events or file hashes.

If you're interested in learning more about osquery, visit the `GitHub project
<https://github.com/facebook/osquery>`_, the `website <https://osquery.io>`_, and
the `users guide <https://osquery.readthedocs.org/>`_.

What is osquery-python?
-----------------------

.. image:: https://travis-ci.org/osquery/osquery-python.svg?branch=master
  :target: https://travis-ci.org/osquery/osquery-python

In osquery, SQL tables, configuration retrieval, log handling, etc are implemented
via a simple, robust plugin and extensions API. This project contains the official
Python bindings for creating osquery extensions in Python. Consider the following
example:

Example walkthrough
-------------------
1. Launch ``osqueryi`` from a terminal window. When osqueryi is run without any
options it will create and connect to a unix socket file in $HOME/.osquery/shell.em.

2. Copy the following code into a file named example.py

.. code-block:: python

  import osquery

  @osquery.register_plugin
  class MyTablePlugin(osquery.TablePlugin):
      def name(self):
          return "foobar"

      def columns(self):
          return [
              osquery.TableColumn(name="foo", type=osquery.STRING),
              osquery.TableColumn(name="baz", type=osquery.STRING),
          ]

      def generate(self, context):
          query_data = []

          for _ in range(2):
              row = {}
              row["foo"] = "bar"
              row["baz"] = "baz"
              query_data.append(row)

          return query_data

  if __name__ == "__main__":
      osquery.start_extension(name="my_awesome_extension",
                              version="1.0.0",)

This will register a table called "foobar" that will
return two rows.

3. Run the example.py script using the --socket option to specify connecting
to the socket file in your home directory. ``python example.py --socket ~/.osquery/shell.em``

4. In the running osqueryi window, enter the follow query:

.. code-block:: none

  osquery> select * from foobar;
  +-----+-----+
  | foo | baz |
  +-----+-----+
  | bar | baz |
  | bar | baz |
  +-----+-----+
  osquery>



This is obviously a contrived example, but it's easy to imagine the
possibilities.

Using the instructions found on the `wiki
<https://osquery.readthedocs.org/en/latest/development/osquery-sdk/#extensions>`_,
you can easily deploy your extension with an existing osquery deployment.

Extensions are the core way that you can extend and customize osquery. At
Facebook, we use extensions extensively to implement many plugins that take
advantage of internal APIs and tools.

Install
-------

This module is currently in "beta mode". We're testing the API and UX before
uploading the module to PyPI.

To install, clone this repo and run the following:

.. code-block:: none

  python setup.py build
  python setup.py install

Alternatively, if you don't want to clone the repo, you can simply:

.. code-block:: none

  pip install git+git://github.com/osquery/osquery-python.git

Development
-----------
See `CONTRIBUTING.md <https://github.com/osquery/osquery-python/blob/master/CONTRIBUTING.md>`_
and the `osquery wiki <https://osquery.readthedocs.org>`_ for development information.

Vulnerabilities
---------------

Facebook has a `bug bounty <https://www.facebook.com/whitehat/>`_ program that
includes osquery. If you find a security vulnerability in osquery, please
submit it via the process outlined on that page and do not file a public issue.
For more information on finding vulnerabilities in osquery, see a recent blog
post about `bug-hunting osquery
<https://www.facebook.com/notes/facebook-bug-bounty/bug-hunting-osquery/954850014529225>`_.
