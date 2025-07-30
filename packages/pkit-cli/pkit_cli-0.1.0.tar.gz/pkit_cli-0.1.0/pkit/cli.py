# pkit/cli.py

import argparse
from pkit import scanner, storage, tracker, vulndb, reporter, fix

def cmd_init(args):
    pkgs = scanner.scan_installed_packages()
    storage.save_snapshot(pkgs)
    print("[pkit] Snapshot saved.")

def cmd_check(args):
    old = storage.load_snapshot()
    new = scanner.scan_installed_packages()
    changes = tracker.compare_snapshots(old, new)
    reporter.print_changes(changes)

def cmd_scan(args):
    pkgs = scanner.scan_installed_packages()
    vulns = vulndb.check_vulnerabilities(pkgs)
    # 저장 시 패키지 + 취약점 정보를 같이 저장
    storage.save_snapshot({
        "packages": pkgs,
        "vulnerabilities": vulns
    })
    reporter.print_vulnerabilities(vulns)

def cmd_report(args):
    pkgs = scanner.scan_installed_packages()
    reporter.generate_report(pkgs)

def cmd_fix(args):
    fix.fix_vulnerabilities()

def cmd_run(args):
    print("[pkit] Running full pipeline...")
    cmd_check(args)
    cmd_scan(args)
    cmd_fix(args)
    cmd_report(args)

def main():
    parser = argparse.ArgumentParser(prog="pkit", description="Python Package Toolkit")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("init", help="Save snapshot of installed packages").set_defaults(func=cmd_init)
    sub.add_parser("check", help="Check for changes since last snapshot").set_defaults(func=cmd_check)
    sub.add_parser("scan", help="Scan for known vulnerabilities").set_defaults(func=cmd_scan)
    sub.add_parser("report", help="Generate a summary report").set_defaults(func=cmd_report)
    sub.add_parser("fix", help="Fix known vulnerabilities by upgrading packages").set_defaults(func=cmd_fix)
    sub.add_parser("run", help="Run check, scan, and report").set_defaults(func=cmd_run)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
