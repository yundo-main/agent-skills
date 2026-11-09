# 03_apply — 스킬 적용: 어떻게 행동시키는가 (완성형)

선택된 스킬 본문+L3 리소스를 system 프롬프트로 주입해 절차대로 수행하게 한다.

## 실행

```bash
cd 03_apply && python3 main.py    # DEEPSEEK_API_KEY 필요 (루트 .env)
```

## 파일

| 파일 | 역할 |
| --- | --- |
| `main.py` | 진입점 — /code-review 리뷰 + svg-diagram 산출물 실습 |
| `apply.py` | 새 층 — build_prompt(L2+L3→system) · run_apply/run_review 파이프라인 |
| `deepseek_agent.py` | 새 부품 — OpenAI 호환 (user,system)->str 백엔드 |
| `disclosure.py` · `skill_loader.py` · `skills/` | ← 이전 단계 vendored |

## 산출물

- `/code-review` 결과 표 — 스킬이 정한 `[심각도] 위치 — 설명 — 제안` 형식
- `../logs/arch-diagram.svg` — svg-diagram 적용 산출물, XML 검증까지 수행
