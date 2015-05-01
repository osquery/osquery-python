osquery-python
==============

What is osquery?
----------------

osquery exposes an operating system as a high-performance relational database.
This allows you to write SQL-based queries to explore operating system data.
With osquery, SQL tables represent abstract concepts such as running processes,
loaded kernel modules, open network connections, browser plugins, hardware
events or file hashes.

SQL tables are implemented via a simple plugin and extensions API.

What is osquery-python?
-----------------------

This project contains the official Python bindings for creating osquery
extensions in Python. Consider the following example:

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

          for i in range(2):
              row = {}
              row["foo"] = "bar"
              row["baz"] = "baz"
              query_data.append(row)

          return query_data

  if __name__ == "__main__":
      osquery.start_extension()

This will register a table called "foobar". As you can see, the table will
return two rows:

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

Vulnerabilities
---------------

Facebook has a `bug bounty <https://www.facebook.com/whitehat/>`_ program that
includes osquery. If you find a security vulnerability in osquery, please
submit it via the process outlined on that page and do not file a public issue.
For more information on finding vulnerabilities in osquery, see a recent blog
post about `bug-hunting osquery
<https://www.facebook.com/notes/facebook-bug-bounty/bug-hunting-osquery/954850014529225>`_.

Learn more
----------

If you're interested in learning more about osquery, visit the `GitHub project
<https://github.com/facebook/osquery>`_,the `website <https://osquery.io>`_, and
the `users guide <https://osquery.readthedocs.org/>`_.
