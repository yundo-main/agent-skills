"""[실습 2/3] Progressive Disclosure — 진입점
역할: 진입점 — disclosure를 실행해 요청별 로드 토큰을 naive와 비교한다
의존: disclosure (이 디렉터리), skill_loader (vendored — 01_spec)
(이전: 01_spec/main.py · 다음: 03_apply/main.py)
"""

import os

from disclosure import run_naive, run_with_disclosure
from skill_loader import SKILLS_DIR, print_report

DEMO_REQUESTS = [
    "아키텍처 다이어그램 SVG로 만들어줘",  # L3 리소스(양식 규격) 참조 스킬
    "이 파이썬 코드 리뷰해줘",
    "서버 디스크랑 메모리 점검해줘",
    "오늘 날씨 알려줘",  # 트리거 없음 → 스킬 미선택 폴백
]


def main():
    if not os.path.isdir(SKILLS_DIR):
        print(f"[안내] {SKILLS_DIR}/ 디렉터리가 없다 — 각 단계는 독립 프로젝트다")
        print("       cd 02_disclose && python3 main.py 로 실행하라")
        return
    naive = run_naive()  # 대조군: 전량 로드 비용은 요청과 무관 — 루프 밖 1회
    rows = []
    for req in DEMO_REQUESTS:
        # L1(상시 메타) → 트리거 → L2(본문) → L3(참조 리소스), 층별 토큰 반환
        r = run_with_disclosure(req)
        saved = f"{100 * (1 - r['total'] / naive):.0f}%" if naive else "-"
        print(f"[disclose] {req} → skill={r['skill']} score={r['score']} "
              f"(L1 {r['l1']} + L2 {r['l2']} + L3 {r['l3']} = {r['total']} "
              f"vs naive {naive})")
        rows.append([req, r["skill"], r["l1"], r["l2"], r["l3"],
                     naive, r["total"], saved])
    print_report("Progressive Disclosure vs 전량 로드",
                 ["요청", "선택", "L1", "L2", "L3", "naive", "공개", "절감"],
                 rows,
                 footer="L1=메타 상시 · L2=본문(트리거 시) · L3=리소스(참조 시)")
    print("→ 다음 단계: cd ../03_apply && python3 main.py")


if __name__ == "__main__":
    main()
