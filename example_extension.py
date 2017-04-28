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
    osquery.start_extension(name="my_awesome_extension",
                            version="1.0.0",)
