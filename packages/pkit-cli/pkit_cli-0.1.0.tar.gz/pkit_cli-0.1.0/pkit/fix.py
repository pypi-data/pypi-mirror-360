import subprocess
import os
from pkit import scanner, vulndb, storage, reporter

def fix_vulnerabilities():
    snapshot_file = storage.SNAPSHOT_FILE

    if not os.path.exists(snapshot_file):
        print(f"[pkit] {snapshot_file} not found. Run 'pkit scan' first.")
        return

    data = storage.load_snapshot()
    packages = data.get("packages", {})
    vulns = data.get("vulnerabilities", {})

    if not vulns:
        print("[pkit] No vulnerable packages found.")
        return

    print("[pkit] Fixing vulnerable packages...\n")

    updated = {}

    for pkg in vulns.keys():
        try:
            print(f"[pkit] Upgrading {pkg}...")
            subprocess.run(["pip", "install", "--upgrade", pkg], check=True)
            updated[pkg] = None  # placeholder
        except subprocess.CalledProcessError:
            print(f"[pkit] Failed to upgrade {pkg}")

    if not updated:
        print("[pkit] No packages upgraded.")
        return

    # 다시 스캔해서 업그레이드된 패키지 버전 확인
    new_pkgs = scanner.scan_installed_packages()
    for pkg in updated:
        if pkg in new_pkgs:
            updated[pkg] = new_pkgs[pkg]

    # 전체 패키지 목록 업데이트
    packages.update(updated)

    # 업그레이드한 패키지들만 대상으로 취약점 다시 검사
    new_vulns = vulndb.check_vulnerabilities(updated)

    # 최신 상태로 저장
    data["packages"] = packages
    data["vulnerabilities"] = new_vulns
    storage.save_snapshot(data)

    print("\n[pkit] Fix complete.")
    
    # 남은 취약점 출력
    if new_vulns:
        print("\n[pkit] Remaining vulnerable packages:")
        reporter.print_vulnerabilities(new_vulns)
    else:
        print("\n[pkit] All vulnerabilities fixed!")