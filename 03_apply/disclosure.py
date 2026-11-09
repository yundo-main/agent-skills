"""[실습 2/3] Progressive Disclosure — 새 층 모듈 (진입점은 main.py)
역할: 부품 — 요청에 맞는 스킬만 L1→L2→L3 순으로 로드해 컨텍스트를 절약한다
의존: skill_loader (vendored — 01_spec)
추가: select_skill, load_level2, load_level3,
     run_with_disclosure, run_naive

Progressive Disclosure의 세 층과 이 모듈 함수의 대응:
  L1  상시 공개   — 모든 유효 스킬의 name+description (메타만, 항상 컨텍스트에)
  L2  트리거 시   — 선택된 스킬 1개의 SKILL.md 본문 = load_level2
  L3  참조 시     — 본문이 가리키는 번들 리소스 = load_level3
비용 비교 기준선은 run_naive(전량 로드)다.
"""

import os
from skill_loader import (SKILLS_DIR, estimate_tokens, list_resources,
                          scan_skills)

SELECT_MIN_SCORE = 2  # 트리거로 인정할 최소 바이그램 겹침 수 — 이보다 낮으면 미선택


def _bigrams(text):
    """한국어 키워드 매칭용 문자 바이그램 집합을 만든다.

    공백 토큰화는 한국어 조사·어미 변화에 약하다 — "리뷰해줘"/"리뷰한다"도
    바이그램 {리뷰,뷰해,해줘}/{리뷰,뷰한,한다}로 겹치는 부분(리뷰,뷰..)이 생긴다.
    파일 내부 전용 헬퍼.
    """
    return {text[i:i + 2] for i in range(len(text) - 1)}


def select_skill(request, skills):
    """요청에 가장 잘 맞는 스킬 하나를 고른다. (SkillResult|None, score) 반환.

    실제 하니스에서는 모델이 L1(name+description)만 보고 고른다 —
    여기서는 같은 판단을 결정론적으로 흉내 낸다:
    요청 문자 바이그램이 스킬의 name+description에 얼마나 겹치는지를 점수화.
    description이 유일한 검색 인덱스라는 것을 보여 주는 교육용 근사치다.
    최저 점수(SELECT_MIN_SCORE) 미만이면 None — 스킬 미선택 폴백.
    """
    best, best_score = None, 0
    for s in skills:
        if s.status != "ok":      # 명세 실패 스킬은 트리거 대상에서 제외
            continue
        hay = s.meta["name"] + " " + s.meta["description"]
        score = sum(1 for bg in _bigrams(request) if bg in hay)
        if score > best_score:
            best, best_score = s, score
    return (best if best_score >= SELECT_MIN_SCORE else None), best_score


def load_level2(skill):
    """L2 — 트리거된 스킬의 본문(SKILL.md 절차)만 로드한다.

    이미 01에서 파싱된 SkillResult.body를 돌려줄 뿐이지만,
    'L2 공개 시점'이라는 의미를 코드에 남기기 위해 함수로 분리했다.
    """
    return skill.body


def load_level3(skill):
    """L3 — 선택된 스킬의 번들 리소스를 읽어 {상대경로: 내용}으로 돌려준다.

    진짜 Progressive Disclosure는 본문이 참조한 파일만 읽는다 —
    이 데모의 스킬들은 본문이 모든 리소스를 참조하므로 목록 전체를 읽는 것과
    결과가 같다. (참조 경로 추출은 수정 과제 수준의 확장)
    """
    out = {}
    for rel in list_resources(skill.path):
        with open(os.path.join(skill.path, rel), encoding="utf-8") as f:
            out[rel] = f.read()
    return out


def run_with_disclosure(request, scanner=scan_skills):
    """요청 하나를 L1→L2→L3 순으로 처리하고 층별 토큰 비용을 돌려준다.

    scanner를 인자로 받는 이유: 다음 층(03_apply)이 스캔 로직을 재구현하지
    않고 이 함수를 합성할 수 있게 하기 위해서다 — vendored 모듈에
    죽은 코드를 남기지 않는 교체 인자 패턴.

    Returns dict: request, skill(선택명|"-"), score, l1, l2, l3, total.
    """
    skills = scanner(SKILLS_DIR)
    ok_skills = [s for s in skills if s.status == "ok"]
    # L1: 모든 유효 스킬의 메타만 상시 공개 — 스킬 수에만 비례
    l1 = sum(estimate_tokens(f"{s.meta['name']}: {s.meta['description']}")
             for s in ok_skills)
    skill, score = select_skill(request, ok_skills)
    # L2·L3: 선택된 스킬에만 지출 — 미선택이면 둘 다 0
    l2 = estimate_tokens(load_level2(skill)) if skill else 0
    l3 = sum(estimate_tokens(t) for t in load_level3(skill).values()) if skill else 0
    return {"request": request, "skill": skill.name if skill else "-",
            "score": score, "l1": l1, "l2": l2, "l3": l3,
            "total": l1 + l2 + l3}


def run_naive(scanner=scan_skills):
    """대조군: 모든 스킬의 명세 원문+리소스를 통째로 올린 비용을 돌려준다.

    요청과 무관하게 일정하므로 main.py는 루프 밖에서 한 번만 호출한다.
    '스킬을 컨텍스트에 전부 올리면 안 되는 이유'를 수치로 보여 주는 기준선.
    """
    total = 0
    for s in scanner(SKILLS_DIR):
        if s.status != "ok":
            continue
        total += estimate_tokens(s.raw)
        total += sum(estimate_tokens(t) for t in load_level3(s).values())
    return total
