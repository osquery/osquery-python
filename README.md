## osquery-python

![osquery-python-logo](https://i.imgur.com/9Vy2GFx.png)

[osquery](https://github.com/facebook/osquery) exposes an operating system as a high-performance relational database. This allows you to write SQL-based queries to explore operating system data. With osquery, SQL tables represent abstract concepts such as running processes, loaded kernel modules, open network connections, browser plugins, hardware events or file hashes.

If you're interested in learning more about osquery, visit the [GitHub project](https://github.com/facebook/osquery), the [website](https://osquery.io), and the [users guide](https://osquery.readthedocs.org/).

### What is osquery-python?

[![Build Status](https://travis-ci.org/osquery/osquery-python.svg?branch=master)](https://travis-ci.org/osquery/osquery-python)

In osquery, SQL tables, configuration retrieval, log handling, etc are implemented via a simple, robust plugin and extensions API. This project contains the official Python bindings for creating osquery extensions in Python. Consider the following example:

```python
#!/usr/bin/env python

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
    osquery.start_extension(name="my_awesome_extension", version="1.0.0")
```

To test this code start an osquery shell:

```
osqueryi --nodisable_extensions
osquery> select value from osquery_flags where name = 'extensions_socket';
+-----------------------------------+
| value                             |
+-----------------------------------+
| /Users/USERNAME/.osquery/shell.em |
+-----------------------------------+
```

Then start the Python extension:

```
python ./my_table_plugin.py --socket /Users/USERNAME/.osquery/shell.em
```

Alternatively, you can also autoload your extension when starting an osquery shell:

```
osqueryi --extension path_to_my_table_plugin.py
```

This will register a table called "foobar". As you can see, the table will return two rows:

```
osquery> select * from foobar;
+-----+-----+
| foo | baz |
+-----+-----+
| bar | baz |
| bar | baz |
+-----+-----+
osquery>
```

This is obviously a contrived example, but it's easy to imagine the possibilities.

Using the instructions found on the [wiki](https://osquery.readthedocs.org/en/latest/development/osquery-sdk/), you can easily deploy your extension with an existing osquery deployment.

Extensions are the core way that you can extend and customize osquery. At Facebook, we use extensions extensively to implement many plugins that take advantage of internal APIs and tools.

### Execute queries in Python

The same Thrift bindings can be used to create a Python client for the `osqueryd` or `osqueryi`'s extension socket. There are helper classes provided that spawn an ephemeral osquery process for consecutive or long running client instances.

```python
import osquery

if __name__ == "__main__":
    # Spawn an osquery process using an ephemeral extension socket.
    instance = osquery.SpawnInstance()
    instance.open()  # This may raise an exception

    # Issues queries and call osquery Thrift APIs.
    instance.client.query("select timestamp from time")
```

### Connect to an existing socket

In the example above the `SpawnInstance()` method is used to fork and configure an osquery instance. We can use similar APIs to connect to the Thrift socket of an existing osquery instance. Remember, normal UNIX permissions apply to the Thrift socket.

Imagine if you started `osqueryd`:
```sh
$ osqueryd --ephemeral --disable_logging --disable_database \
    --extensions_socket /home/you/.osquery/osqueryd.sock &
```

Then use the Python bindings:
```python
import osquery

if __name__ == "__main__":
    # You must know the Thrift socket path
    # For an installed and running system osqueryd, this is:
    #   Linux and macOS: /var/osquery/osquery.em
    #   FreeBSD: /var/run/osquery.em
    #   Windows: \\.pipe\osquery.em
    instance = osquery.ExtensionClient('/home/you/.osquery/osqueryd.sock')
    instance.open()  # This may raise an exception

    # Issue queries and call osquery Thrift APIs.
    client = instance.extension_client()
    client.query('select timestamp from time')
```

### Install

To install from PyPi, run the following:

```
pip install osquery
```

Alternatively, to install from this repo, run the following:

```
python setup.py build
python setup.py install
```


### Development

See [CONTRIBUTING.md](https://github.com/osquery/osquery-python/blob/master/CONTRIBUTING.md) and the [osquery wiki](https://osquery.readthedocs.org) for development information.

### Vulnerabilities

Facebook has a [bug bounty](https://www.facebook.com/whitehat/) program that includes osquery. If you find a security vulnerability in osquery, please submit it via the process outlined on that page and do not file a public issue. For more information on finding vulnerabilities in osquery, see a recent blog post about [bug-hunting osquery](https://www.facebook.com/notes/facebook-bug-bounty/bug-hunting-osquery/954850014529225).
