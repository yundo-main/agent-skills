---
name: code-review
description: 코드를 보안·정확성·성능·가독성 순으로 리뷰한다. "/code-review", "리뷰해줘", "코드 검토" 요청에 사용한다.
---

# Code Review 절차

1. 대상 코드를 끝까지 읽고 의도를 한 문장으로 파악한다.
2. 아래 순서대로 문제를 찾는다: 보안 → 정확성 → 성능 → 가독성.
3. 문제마다 `[심각도] 위치 — 설명 — 수정 제안` 한 줄로 적는다.
4. 심각도는 critical / major / minor 셋만 쓴다.
5. 문제가 없으면 "이상 없음"이라고만 답한다.

상세 기준은 `checklists/review-checklist.md`를 읽어 적용한다.
