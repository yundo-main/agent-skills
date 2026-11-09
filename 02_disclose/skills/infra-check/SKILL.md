---
name: infra-check
description: 서버의 디스크·메모리·프로세스 상태를 점검한다. "인프라 점검", "서버 상태 확인", "디스크 확인" 요청에 사용한다.
---

# Infra Check 절차

1. 디스크 사용률 → 메모리 → 고CPU/좀비 프로세스 순으로 확인한다.
2. 각 항목을 ok / warn / crit 으로 판정한다 (임계값은 `checklists/infra-thresholds.md` 참조).
3. warn 이상인 항목만 원인 가설과 조치 명령을 함께 제안한다.
4. 마지막에 "요약: N개 warn, M개 crit" 한 줄을 붙인다.
