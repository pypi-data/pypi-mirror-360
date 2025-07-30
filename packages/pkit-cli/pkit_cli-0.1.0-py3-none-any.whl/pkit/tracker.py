# pkit/tracker.py

def compare_snapshots(old, new):
    added = {}
    removed = {}
    updated = {}

    for pkg in new:
        if pkg not in old:
            added[pkg] = new[pkg]
        elif new[pkg] != old[pkg]:
            updated[pkg] = {"old": old[pkg], "new": new[pkg]}

    for pkg in old:
        if pkg not in new:
            removed[pkg] = old[pkg]

    return {"added": added, "removed": removed, "updated": updated}
