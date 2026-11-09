"""[실습 1/3] SKILL.md 명세 — 진입점
역할: 진입점 — skill_loader로 스킬을 발견·검증해 인벤토리 보고서를 출력한다
의존: skill_loader (이 디렉터리)
(다음: 02_disclose/main.py)
"""

import os

from skill_loader import (SKILLS_DIR, estimate_tokens, list_resources,
                          print_report, scan_skills)


def main():
    if not os.path.isdir(SKILLS_DIR):
        print(f"[안내] {SKILLS_DIR}/ 디렉터리가 없다 — 각 단계는 독립 프로젝트다")
        print("       cd 01_spec && python3 main.py 로 실행하라")
        return
    # 발견·파싱·검증을 한 호출로 — skills/ 아래 모든 스킬의 인벤토리
    skills = scan_skills(SKILLS_DIR)
    for s in skills:
        mark = "ok" if s.status == "ok" else f"error: {s.error}"
        print(f"[scan] {s.name:<16} {mark}")
    # res 열: 번들 리소스 수 — 다음 단계의 L3 대상을 미리 보여 주는 복선
    rows = [[s.name, s.status, len(s.meta), s.n_bytes,
             estimate_tokens(s.body) if s.status == "ok" else "-",
             len(list_resources(s.path))]
            for s in skills]
    ok = sum(1 for s in skills if s.status == "ok")
    print_report("스킬 인벤토리",
                 ["skill", "status", "fields", "bytes", "~tokens", "res"],
                 rows,
                 footer=f"유효 {ok}/{len(skills)} · res=번들 리소스 수(L3 대상)")
    print("→ 다음 단계: cd ../02_disclose && python3 main.py")


if __name__ == "__main__":
    main()
