import json
import sys

from db import get_store

store = get_store()


def upload_bundles(bundle_files):
    for bundle_file in bundle_files:
        with open(bundle_file) as raw_json:
            bundle = json.load(raw_json)
            store.upload_bundle(bundle)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"USAGE: python {sys.argv[0]} <bundleFile.json> [<bundle2.json>...].")
        sys.exit(1)

    upload_bundles(sys.argv[1:])
