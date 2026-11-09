# 02_disclose — Progressive Disclosure: 언제 로드하는가

요청에 맞는 스킬만 L1→L2→L3 순으로 로드해 컨텍스트를 절약한다.

## 실행

```bash
cd 02_disclose && python3 main.py
```

## 파일

| 파일 | 역할 |
| --- | --- |
| `main.py` | 진입점 — 요청별 공개 토큰 vs naive 비교 |
| `disclosure.py` | 새 층 — 트리거 선택 + L1/L2/L3 로딩 + naive 대조군 |
| `skill_loader.py` | ← 01_spec vendored (이름·내용 동일) |
| `skills/` | ← 01_spec vendored |

## 핵심

- **L1** name+description 상시 → **L2** 본문(트리거 시) → **L3** 리소스(참조 시)
- `select_skill`은 description만으로 판단 — description이 유일한 검색 인덱스
- 보고서: 공개 비용은 요청에 비례, 스킬 수에는 거의 무관 (실측 55~89% 절감)
