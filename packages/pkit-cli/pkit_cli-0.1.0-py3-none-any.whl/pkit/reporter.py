# pkit/reporter.py

def print_changes(changes):
    print("\n[pkit] Package changes since last snapshot:")
    for category in ["added", "removed", "updated"]:
        entries = changes.get(category, {})
        if entries:
            print(f"\n{category.upper()}:")
            for name, info in entries.items():
                if category == "updated":
                    print(f"  - {name}: {info['old']} → {info['new']}")
                else:
                    print(f"  - {name}: {info}")

def print_vulnerabilities(vulns):
    if not vulns:
        print("\n[pkit] No known vulnerabilities found.")
        return
    print("\n[pkit] Vulnerable packages detected:")
    for pkg, cves in vulns.items():
        print(f"  - {pkg}: {', '.join(cves)}")

def generate_report(pkgs):
    print("\n[pkit] Installed packages summary:")
    for name, version in sorted(pkgs.items()):
        print(f"  - {name}=={version}")
