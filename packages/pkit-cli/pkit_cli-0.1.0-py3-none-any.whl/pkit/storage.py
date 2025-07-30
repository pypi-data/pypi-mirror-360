# pkit/storage.py

import json
import os

SNAPSHOT_FILE = "pkit_snapshot.json"

def save_snapshot(data):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_snapshot():
    if not os.path.exists(SNAPSHOT_FILE):
        print("[pkit] No snapshot found. Run 'pkit init' first.")
        return {}
    with open(SNAPSHOT_FILE, "r") as f:
        return json.load(f)
