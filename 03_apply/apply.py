"""[실습 3/3] 스킬 적용 (/code-review) — 새 층 모듈 (진입점은 main.py)
역할: 부품 — 선택된 스킬 본문을 시스템 프롬프트로 주입해 절차대로 수행하게 한다
의존: disclosure (vendored — 02_disclose), skill_loader (vendored — 01_spec),
    deepseek_agent (이 디렉터리)
추가: build_prompt, run_with_skill, run_review, REVIEW_REQUEST

'로드'와 '적용'은 다르다 — 02가 스킬을 찾아 읽어온 것이 로드라면,
이 층은 그 절차를 에이전트의 '일하는 방식'으로 승격시키는 주입이다.
"""

import time
from deepseek_agent import deepseek_agent
from disclosure import load_level3, run_with_disclosure
from skill_loader import SKILLS_DIR, scan_skills

REVIEW_REQUEST = "이 코드 리뷰해줘"  # code-review 스킬 트리거용 고정 요청


def build_prompt(skill, target, instruction="다음 코드를 리뷰하라",
                 resources=None):
    """스킬 본문+L3 리소스 → system(절차), 대상 → user(작업물)로 조립한다.

    system은 '이 대화의 일하는 방식'을 선언하는 자리라 절차 지식이 가장 잘 먹힌다.
    resources(L3)는 본문이 참조한 번들 문서 — 양식 규격·체크리스트 같은
    '메타프롬프트 부품'으로, 본문 뒤에 이어 붙여 실제로 주입되게 한다.
    """
    system = skill.body
    if resources:  # L3: {상대경로: 내용} — 경로를 붙여 '어떤 파일인지'도 전달
        system += "\n\n" + "\n\n".join(
            f"## 참조 리소스: {rel}\n{txt}" for rel, txt in resources.items())
    user = f"{instruction}:\n\n```\n{target}\n```"
    return system, user


def run_with_skill(target, skill, agent=deepseek_agent,
                   instruction="다음 코드를 리뷰하라", resources=None):
    """스킬 절차를 에이전트에 입혀 실행하고 결과를 구조화해 돌려준다.

    agent를 인자로 받아 백엔드를 교체한다 — 스킬은 텍스트라 모델에 종속되지 않는다.
    결과 dict: status(ok|error), output(사용자용 정제 문구),
    error(내부용 원인 — output과 분리), elapsed_ms.
    """
    system, user = build_prompt(skill, target, instruction, resources)
    t0 = time.time()
    try:
        output = agent(user, system=system)
        status, error = "ok", ""
    except Exception as e:  # 내부용 원인은 error에 — 사용자 문구와 분리
        output, status, error = "", "error", str(e)
    return {"status": status, "output": output, "error": error,
            "elapsed_ms": int((time.time() - t0) * 1000)}


def run_apply(request, target, agent=deepseek_agent,
              instruction="다음 코드를 리뷰하라"):
    """요청 → 스킬 선택·공개(L1~L3) → system 주입·실행 — 스킬 무관 파이프라인.

    02가 '로드했다'고 계산한 L3 리소스까지 실제로 system에 주입한다 —
    공개된 지식은 전부 절차가 된다. run_review는 이 함수의 리뷰용 래퍼다.
    """
    d = run_with_disclosure(request)
    skill = {s.name: s for s in scan_skills(SKILLS_DIR)}.get(d["skill"])
    if skill is None:
        return {"status": "error", "output": "", "elapsed_ms": 0,
                "error": "트리거된 스킬 없음", "disclosed": d["total"],
                "skill": "-"}
    r = run_with_skill(target, skill, agent=agent, instruction=instruction,
                       resources=load_level3(skill))
    r["disclosed"] = d["total"]
    r["skill"] = d["skill"]
    return r


def run_review(target, agent=deepseek_agent):
    """스캔(01)→선택·공개(02)→주입·실행(03) 전체 파이프라인 — 리뷰용 래퍼."""
    return run_apply(REVIEW_REQUEST, target, agent=agent)
