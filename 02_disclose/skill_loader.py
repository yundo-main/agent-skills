"""[공용] 스킬 로더 — SKILL.md 발견·파싱·검증 + 공통 보고서
역할: 부품 — 이 과정의 뼈대. 실행은 main.py에서 한다
의존: 없음 (표준 라이브러리만 사용)
추가: scan_skills, spec_check, split_frontmatter, list_resources,
     estimate_tokens, print_report

이 모듈은 세 가지 책임을 진다 — 모든 단계가 이 파일을 vendoring한다.
  1) 발견·파싱: skills/ 디렉터리를 스캔해 SKILL.md를 meta(프런트매터)+body(절차)로 분리
  2) 검증: 개방 표준의 필수 규칙(필드·형식·길이)을 spec_check로 검사
  3) 공통 도구: 토큰 근사치·번들 리소스 목록·요약 보고서 출력
"""

import os
import re
from dataclasses import dataclass, field

SKILLS_DIR = "skills"              # 스킬 디렉터리가 모여 있는 기본 경로
REQUIRED_FIELDS = ("name", "description")  # 개방 표준의 필수 프런트매터 필드
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # name 규격: 소문자+하이픈
DESC_MAX_CHARS = 1024              # description 최대 길이 (개방 표준)
MAX_BODY_LINES = 500               # 본문 권장 상한 — 넘으면 상세를 L3 리소스로 나눌 것
CHARS_PER_TOKEN = 4                # 토큰 근사치: 문자 4개 ≈ 1토큰 (절감 비교용)


@dataclass
class SkillResult:
    """스킬 하나의 발견·파싱·검증 결과를 담는 구조체.

    status가 "error"여도 meta/body는 비어 있을 뿐 예외를 던지지 않는다 —
    실패 원인은 내부용 error 필드에 남기고(사용자 문구와 분리) 스캔을 계속한다.
    """
    name: str                      # 디렉터리명 (검증 전이라 meta.name과 다를 수 있음)
    path: str                      # 스킬 디렉터리 경로 — L3 리소스를 찾는 기준점
    status: str                    # 최종 판정: "ok" | "error"
    meta: dict = field(default_factory=dict)   # 프런트매터 필드들 — L1 공개 대상
    body: str = ""                 # 본문(절차) — L2 공개 대상
    raw: str = ""                  # 파일 원문 전체 — naive 비용 계산용
    error: str = ""                # 내부용 실패 원인 (사용자 출력과 분리)
    n_bytes: int = 0               # 파일 크기(바이트)


def split_frontmatter(text):
    """SKILL.md 원문을 (meta, body)로 분리한다.

    명세상 프런트매터는 파일 첫 줄의 '---'로 시작해 다음 '---'까지다.
    과정 특성상 평탄한 `key: value` 행만 파싱한다(표준 라이브러리만 사용) —
    중첩 YAML이 필요하면 파서가 아니라 의존성 추가로 해결한다.

    Returns: (meta: dict, body: str). 프런트매터가 없으면 meta={}.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta, end = {}, None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end = i
            break
        if ":" in line:  # 'key: value' 행만 채택 — 그 외 행은 무시
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    if end is None:                # 닫는 '---'가 없으면 프런트매터가 아님
        return {}, text
    return meta, "\n".join(lines[end + 1:]).strip()


def spec_check(dir_path):
    """SKILL.md 한 개를 읽어 명세 규칙으로 검사해 SkillResult를 돌려준다.

    검사 규칙(모두 개방 표준·하니스 요구사항에서 옴):
      - SKILL.md 파일이 디렉터리에 존재하는가
      - 필수 필드(name, description)가 비어 있지 않은가
      - name이 소문자+하이픈 패턴인가
      - name이 디렉터리명과 일치하는가 (경로 = 식별자)
      - description이 1024자 이하인가 (L1 비용 상한)
      - 본문(절차)이 비어 있지 않은가 — 가르칠 내용이 없으면 스킬이 아님
      - 본문이 500줄 이하인가 — 넘으면 상세는 L3 리소스로 분리 신호
    """
    name = os.path.basename(dir_path)
    path = os.path.join(dir_path, "SKILL.md")
    if not os.path.isfile(path):
        return SkillResult(name, dir_path, "error", error="SKILL.md 없음")
    text = open(path, encoding="utf-8").read()
    meta, body = split_frontmatter(text)
    errors = []
    missing = [f for f in REQUIRED_FIELDS if not meta.get(f)]
    if missing:
        errors.append("필수 필드 없음: " + ", ".join(missing))
    if meta.get("name") and not NAME_PATTERN.match(meta["name"]):
        errors.append(f"name 형식 위반: {meta['name']}")
    if meta.get("name") and meta["name"] != name:
        errors.append(f"name({meta['name']}) != 디렉터리명({name})")
    if len(meta.get("description", "")) > DESC_MAX_CHARS:
        errors.append(f"description {DESC_MAX_CHARS}자 초과")
    if not body.strip():
        errors.append("본문(절차)이 비어 있음")
    if len(body.splitlines()) > MAX_BODY_LINES:
        errors.append(f"본문 {MAX_BODY_LINES}줄 초과")
    return SkillResult(name, dir_path, "ok" if not errors else "error",
                       meta, body, text, "; ".join(errors),
                       len(text.encode("utf-8")))


def scan_skills(root=SKILLS_DIR):
    """root 아래 모든 스킬 디렉터리를 검사해 SkillResult 리스트로 돌려준다.

    발견·파싱·검증을 한 호출로 묶은 인벤토리 함수 —
    02의 트리거 판단과 03의 스킬 조회도 이 결과를 그대로 쓴다.
    하위 디렉터리가 하나도 없으면 빈 리스트를 돌려준다.
    """
    if not os.path.isdir(root):
        return []
    return [spec_check(os.path.join(root, d))
            for d in sorted(os.listdir(root))
            if os.path.isdir(os.path.join(root, d))]


def list_resources(dir_path):
    """SKILL.md를 제외한 번들 리소스의 상대 경로 목록을 돌려준다.

    본문이 참조하는 상세 문서·체크리스트·스크립트가 L3 대상이다 —
    checklists/, rules/, scripts/ 등 어떤 하위 경로든 모은다.
    """
    out = []
    for base, _, files in os.walk(dir_path):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(base, f), dir_path)
            if rel != "SKILL.md":
                out.append(rel)
    return sorted(out)


def estimate_tokens(text):
    """문자 수 기반 토큰 근사치를 돌려준다.

    정확한 토크나이저가 아니라 '전량 로드 vs 점진 공개' 비율 비교용 —
    절감률(%)만 일관되면 근사치로 충분하다.
    """
    return max(1, len(text) // CHARS_PER_TOKEN)


def print_report(title, columns, rows, footer=""):
    """모든 단계가 vendoring해 쓰는 공통 요약 보고서를 출력한다.

    실행 로그(중간 과정)와 분리해 마지막에 표로 요약한다 —
    결과를 보려고 로그를 거슬러 올라가지 않게 하는 장치.
    columns·rows는 단계마다 달라지고, 함수는 바뀌지 않는다.
    """
    print("\n" + "=" * 72)
    print(f"[보고서] {title}")
    print("=" * 72)
    print(" | ".join(columns))
    print("-" * 72)
    for r in rows:
        print(" | ".join(str(c) for c in r))
    if footer:
        print("-" * 72)
        print(footer)
    print("=" * 72 + "\n")
