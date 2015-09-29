#!/usr/bin/env python
"""
simple script which runs a query from the command-line
"""

import sys
import osquery

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: %s \"query\"" % sys.argv[0])
        sys.exit(1)
    CLIENT = osquery.ExtensionClient()
    CLIENT.open()
    RESULTS = CLIENT.extension_client().query(sys.argv[1])
    if RESULTS.status.code != 0:
        print("Error running the query: %s" % RESULTS.status.message)
        sys.exit(1)

    for row in RESULTS.response:
        print("=" * 80)
        for key, val in row.iteritems():
            print("%s => %s" % (key, val))
    if len(RESULTS.response) > 0:
        print("=" * 80)
