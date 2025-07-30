# pkit/vulndb.py

import requests
import time

def check_vulnerabilities(packages):
    found = {}

    for name, version in packages.items():
        payload = {
            "package": {
                "name": name,
                "ecosystem": "PyPI"
            },
            "version": version
        }
        try:
            print(f"[pkit] Checking {name}=={version}...")
            response = requests.post(
                "https://api.osv.dev/v1/query",
                json=payload,
                timeout=3  # 짧게 대기
            )
            response.raise_for_status()
            data = response.json()
            vulns = data.get("vulns", [])
            if vulns:
                cves = [vuln.get("id") for vuln in vulns]
                found[name] = cves
        except requests.exceptions.Timeout:
            print(f"[timeout] {name} 요청이 너무 오래 걸립니다. 생략합니다.")
        except requests.exceptions.RequestException as e:
            print(f"[error] {name} 요청 중 오류 발생: {e}")
        time.sleep(0.3)  # 너무 빠른 연속 요청 방지 (rate limit 우회)

    return found
