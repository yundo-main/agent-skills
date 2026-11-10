"""[실습 3/3] 스킬 적용 — 진입점
역할: 진입점 — code-review 스킬로 코드 리뷰, svg-diagram 스킬로 실제 SVG 산출물 생성
의존: apply·deepseek_agent (이 디렉터리), disclosure·skill_loader (vendored)
(이전: 02_disclose/main.py)
"""

import os
import re
import xml.dom.minidom

from apply import build_prompt, run_apply, run_review
from disclosure import load_level3, run_naive
from skill_loader import SKILLS_DIR, print_report, scan_skills

# 리뷰 대상 — samples/ 아래 .py 파일. 스킬이 잡아내도록 의도적 결함을 심어 둠
SAMPLES_DIR = "samples"

# svg-diagram 적용 실습용 — 트리거 요청과 작업 대상, 산출물 경로
SVG_REQUEST = "아키텍처 다이어그램 SVG로 만들어줘"
SVG_TARGET = "3계층 아키텍처(프레젠테이션 · 로직 · 데이터) 다이어그램"
SVG_OUT = "../logs/arch-diagram.svg"   # 학생 실행 산출물은 logs/에 둔다

# infra-check 적용 실습용 — 트리거 요청과 점검 대상 지표(가상 값)
INFRA_REQUEST = "서버 디스크랑 메모리 점검해줘"
INFRA_METRICS = "disk: 91% 사용, mem: 87% 사용, load avg: 2.4, uptime: 45일"


def run_infra_demo():
    """infra-check 스킬 적용 실습 — 가상 지표를 절차대로 점검한 보고 텍스트."""
    r = run_apply(INFRA_REQUEST, INFRA_METRICS,
                  instruction="다음 지표를 스킬 절차대로 점검하라")
    if r["status"] != "ok":
        print(f"[infra] 실패: {r['error']}")
        return
    print(f"[infra] 트리거: {r['skill']} (공개토큰 {r['disclosed']}, "
          f"{r['elapsed_ms']}ms)")
    for ln in r["output"].splitlines()[:4]:
        print(f"        {ln}")


def run_svg_demo():
    """svg-diagram 스킬 적용 실습 — 스킬 절차(생성→저장→검증)를 실제로 수행한다.

    run_apply가 트리거→L3 리소스 포함 system 주입→생성까지 수행하므로
    이 함수는 산출물 추출·저장·검증만 담당한다 — 진입점은 얇게.
    """
    r = run_apply(SVG_REQUEST, SVG_TARGET,
                  instruction="다음 요청을 스킬 절차대로 처리하라")
    if not r["skill"] or r["skill"] == "-":
        return {"status": "error", "error": "svg-diagram 미선택"}
    print(f"[svg] 트리거: {r['skill']} (공개토큰 {r['disclosed']})")
    # 주입된 메타프롬프트 미리보기 — 무엇이 system으로 들어갔는지 보여 준다
    skill = {s.name: s for s in scan_skills(SKILLS_DIR)}[r["skill"]]
    res = load_level3(skill)
    system, _ = build_prompt(skill, SVG_TARGET,
                             "다음 요청을 스킬 절차대로 처리하라", res)
    print(f"[svg] system 주입: L2 본문 + L3 리소스 {len(res)}개")
    for rel, txt in res.items():
        print(f"      L3: {rel} — 발췌:")
        for ln in [l for l in txt.splitlines() if l.strip()][:6]:
            print(f"          {ln}")
    if r["status"] != "ok":
        return {"status": "error", "error": r["error"], "elapsed_ms": r["elapsed_ms"]}
    # 응답에서 <svg> 블록만 추출 — 스킬의 출력 규칙(코드 블록만)을 코드로 강제.
    # 비탐욕 매치로 '첫 완결 블록'만 취한다 — 탐욕 매치는 여러 블록 사이의
    # 잡문(스크립트·설명)까지 삼켜 깨진 XML을 만든다
    m = re.search(r"<svg[\s\S]*?</svg>", r["output"])
    svg = m.group(0) if m else r["output"]
    with open(SVG_OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    try:  # 스킬 절차 3 — XML 파싱으로 산출물 검증
        xml.dom.minidom.parse(SVG_OUT)
        verdict = "ok"
    except Exception as e:
        verdict = str(e)[:40]
    return {"status": "ok", "path": SVG_OUT, "bytes": len(svg),
            "check": verdict, "elapsed_ms": r["elapsed_ms"]}


def main():
    if not os.path.isdir(SKILLS_DIR):
        print(f"[안내] {SKILLS_DIR}/ 디렉터리가 없다 — 각 단계는 독립 프로젝트다")
        print("       cd 03_apply && python3 main.py 로 실행하라")
        return
    naive = run_naive()  # 02의 전량 로드 대조군 — 완성형도 같은 비교를 품는다
    # 관통 실습: svg-diagram — 01 발견 → 02 공개 → 03 적용까지 같은 스킬
    print("\n--- svg-diagram 적용 실습 (생성 → 저장 → 검증) ---")
    res = run_svg_demo()
    if res["status"] == "ok":
        print(f"[svg] {res['path']} 저장 ({res['bytes']}B, {res['elapsed_ms']}ms) "
              f"· XML 검증 {res['check']}")
        print(f"[svg] 열어 보기: open {res['path']}")
    else:
        print(f"[svg] 실패: {res['error']}")
    # 보조 실습 1: infra-check — 지표를 절차대로 점검해 보고 텍스트 생성
    print("\n--- infra-check 적용 데모 ---")
    run_infra_demo()
    # 보조 실습 2: code-review — samples/ 파일을 같은 파이프라인으로 리뷰
    print("\n--- code-review 적용 데모 ---")
    files = sorted(f for f in os.listdir(SAMPLES_DIR) if f.endswith(".py"))
    targets = [(os.path.splitext(f)[0],
                open(os.path.join(SAMPLES_DIR, f), encoding="utf-8").read())
               for f in files]
    results = [run_review(code) for _, code in targets]
    rows = []
    for (label, _), r in zip(targets, results):
        note = (r["output"].splitlines() or [""])[0][:42] if r["status"] == "ok" \
            else r["error"][:42]
        rows.append([label, r["status"], r["disclosed"], naive,
                     r["elapsed_ms"], note])
        print(f"[apply] {label}: {r['status']} "
              f"({r['elapsed_ms']}ms, 공개토큰 {r['disclosed']})")
    print_report("/code-review 적용 결과",
                 ["대상", "status", "공개토큰", "naive", "elapsed_ms", "첫 줄"],
                 rows,
                 footer="스킬 본문이 system 프롬프트로 주입됨 — 02와 동일한 공개 비용")



if __name__ == "__main__":
    main()
