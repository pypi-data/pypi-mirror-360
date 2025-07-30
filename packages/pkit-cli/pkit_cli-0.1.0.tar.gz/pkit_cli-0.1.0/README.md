# pkit — Python Package Inspection Toolkit

**pkit**은 로컬에 설치된 Python 패키지의 상태를 스냅샷으로 저장하고, 변경 사항을 추적하며, 취약점을 스캔하고 자동으로 수정까지 할 수 있는 간단하고 유용한 CLI 도구입니다.

## 기능

- `init`: 현재 설치된 패키지 상태를 저장
- `check`: 이전 상태와 비교해 변경된 패키지 추적
- `scan`: 설치된 패키지에서 알려진 취약점 검색
- `report`: 전체 패키지 상태 리포트 출력
- `fix`: 알려진 취약점이 있는 패키지를 자동 업그레이드
- `run`: `check`, `scan`, `fix`, `report` 순차 실행

---

## 설치

PyPI에 업로드된 후 다음 명령어로 설치할 수 있습니다:

```bash
pip install pkit
