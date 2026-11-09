# 01_spec — SKILL.md 명세: 무엇이 스킬인가

`skills/` 아래 스킬 디렉터리를 스캔·파싱·검증해 인벤토리 보고서를 출력한다.

## 실행

```bash
cd 01_spec && python3 main.py
```

## 파일

| 파일 | 역할 |
| --- | --- |
| `main.py` | 진입점 — 인벤토리 데모 |
| `skill_loader.py` | 부품 — 발견·파싱·검증 + 공통 보고서 (이 과정의 뼈대, 후속 단계가 vendoring) |
| `skills/` | 실습용 스킬 4개 — code-review · infra-check · svg-diagram · bad-example(검증 실패 예시) |

## 핵심

- 프런트매터 `name`+`description` = "언제" · 본문 = "어떻게" · 번들 리소스(res) = L3 대상
- `spec_check`가 필수 필드·name 형식·description 길이·본문 존재를 검사 — 스킬의 품질 게이트
