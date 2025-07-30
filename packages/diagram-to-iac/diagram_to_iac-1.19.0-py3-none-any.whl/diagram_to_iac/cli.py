# src/diagram_to_iac/cli.py

import sys, json
import requests   # external package, so pipreqs must pick it up

def main():
    # a sanity check that our imports actually work:
    print("✅  diagram-to-iac CLI is up and running!")
    print("• requests version:", requests.__version__)
    # verify stdlib too
    data = {"ok": True}
    print("• json dump:", json.dumps(data))
    sys.exit(0)
