# Agent Skills — 디렉터리 구조

```text
skill/
├── 00_intro/                  도입 (슬라이드만)
├── 01_spec/                   기반 — 복사(vendor) 시작점
│   ├── main.py                진입점 — 스킬 인벤토리 데모
│   ├── skill_loader.py        부품 — 발견·파싱·검증 + 공통 보고서 (이 과정의 뼈대)
│   ├── skills/                실습용 스킬 (code-review, infra-check, svg-diagram, bad-example)
│   └── slides/
├── 02_disclose/               + Progressive Disclosure 층
│   ├── main.py                진입점 — 요청별 로드 토큰 비교
│   ├── disclosure.py          새 층 — L1→L2→L3 점진 로딩 + naive 대조군
│   ├── skill_loader.py        ← 01_spec vendored
│   ├── skills/                ← 01_spec vendored
│   └── slides/
├── 03_apply/                  + 스킬 적용 층 (완성형)
│   ├── main.py                진입점 — /code-review 리뷰 데모
│   ├── apply.py               새 층 — 스킬 본문 → system 프롬프트 주입
│   ├── deepseek_agent.py      새 부품 — OpenAI 호환 (str)->str 백엔드
│   ├── disclosure.py          ← 02_disclose vendored
│   ├── skill_loader.py        ← 01_spec vendored
│   ├── skills/                ← 01_spec vendored
│   └── slides/
├── 99_ref/
│   └── slides/                참고자료
├── index.html                 SVG 슬라이드 인덱스
├── .env.example               환경변수 템플릿 (.env는 직접 생성)
├── instructor/                [강사용 전체 — 배포 제외]
├── logs/                      학생 실행 로그 (.gitkeep만 커밋)
├── readme.md
├── .distignore
└── .gitignore
```

## 슬라이드 발표

`index.html`을 열고 `▶ 전체 발표`(전 단계) 또는 각 단계의 `▶ 발표`를 누른다. 카드 썸네일을 누르면 그 슬라이드부터 시작한다.
키보드: `←` `→` 이동 · `Space` 다음 · `Home`/`End` 처음·끝 · `F` 전체화면 · `Esc` 닫기.

## 실습 순서

어떤 단계든 **실행할 파일은 항상 `main.py`** — 디렉터리가 목적을, `main.py`가 진입점을 담당한다.

| 순서 | 폴더 | 실행 파일 | 내용 | 실행 |
| --- | --- | --- | --- | --- |
| 0 | (루트) | `.env.example` → `.env` | API 키 설정 (03만 필요) | `cp .env.example .env` |
| 1 | `01_spec/` | `main.py` | 스킬 발견·파싱·검증 — 인벤토리 보고서 | `cd 01_spec && python3 main.py` |
| 2 | `02_disclose/` | `main.py` | L1→L2→L3 점진 로딩 vs 전량 로드 토큰 비교 | `cd 02_disclose && python3 main.py` |
| 3 | `03_apply/` | `main.py` | code-review 스킬을 에이전트에 주입해 실제 리뷰 | `cd 03_apply && python3 main.py` |

각 `main.py` 1행에는 `(이전: X/main.py · 다음: Y/main.py)`가 있어 다음에 어디로 가면 되는지 보인다.
실행 끝에는 실행 로그와 분리된 `[보고서]` 섹션이 출력된다. `03_apply`는 실행 끝에 svg-diagram 스킬 적용 실습도 수행한다 —
생성된 SVG를 `logs/arch-diagram.svg`로 저장하고 XML로 검증한다.

## 구조 — main.py + vendored 층 모듈

이 방식은 **main 진입점 패턴**(Go의 `cmd/.../main.go`와 유사)과 **vendoring**(이전 단계 모듈을 그대로 복사해 포함)을 결합한 것이다.

1. **모든 디렉터리의 실행 파일은 `main.py`다** — 새로 추가되는 층은 역할이 드러나는 이름의 모듈로 분리하고, `main.py`는 그 모듈을 import해 데모만 실행한다.
2. **이전 단계의 모듈은 이름·내용 그대로 복사(vendor)해 가져온다** — 사본이 원본과 동일함(`diff`로 검증)이 "이전 층을 건드리지 않았다"는 증거다.
3. **각 디렉터리는 별도의 프로젝트로 간주한다** — `sys.path` 조작·디렉터리 밖 import 금지. `cd {단계} && python3 main.py`만으로 실행된다.
4. **다음 층은 이전 층의 함수를 재구현하지 않고, 교체 가능한 인자(`scanner`, `agent`)로 합성한다** — vendored 모듈의 함수가 죽은 코드로 남지 않게 한다.

| 단계 | main.py가 실행 | 새 층 모듈 | vendored |
| --- | --- | --- | --- |
| `01_spec` | 스킬 인벤토리 | — (`skill_loader` 자체가 기준) | 없음 |
| `02_disclose` | 요청별 공개 토큰 비교 | `disclosure.py` | `skill_loader`·`skills/` |
| `03_apply` | /code-review 적용 | `apply.py` (+`deepseek_agent.py` 신규) | `disclosure`·`skill_loader`·`skills/` |
| `99_ref` | — | — | 슬라이드만 |

vendoring은 사슬이다: 각 단계가 직전 단계의 모듈 전부를 품고 새 층 하나를 더하므로, `03_apply`가 자연스럽게 모든 층을 갖춘 **완성형**이 된다.

각 `.py` 파일 맨 위 docstring에 **RD 표기**(`역할:`+`의존:`)로 관계가 적혀 있다.

## 보고서 — 관측 열이 단계마다 깊어진다

`skill_loader.py`의 공통 `print_report(title, columns, rows, footer)`를 모든 단계가 vendoring해 쓴다.
보고서의 행은 단계의 작업 단위(스킬→요청→대상)로 바뀌고, `status`·토큰·시간 같은 관측 열은 단계를 지날수록 더 많은 정보를 담는다.

| 단계 | 행 단위 | 주요 열 |
| --- | --- | --- |
| `01_spec` | 스킬 | `skill, status, fields, bytes, ~tokens, res` |
| `02_disclose` | 요청 | `요청, 선택, L1, L2, L3, naive, 공개, 절감` |
| `03_apply` | 리뷰 대상 | `대상, status, 공개토큰, naive, elapsed_ms, 첫 줄` |

## 배포 규칙

- `instructor/` 폴더 전체는 학생에게 지급하지 않는다 (`.distignore` 참고).
- 단계 폴더는 수업 단위이자 **독립 프로젝트**다 — 어떤 폴더든 단독으로 떼어 줘도 `main.py`로 완결 실행된다.
- 코드 공유는 `shared/` 디렉터리 대신 vendoring으로 해결한다. `logs/`는 코드가 아니라 학생 실행 로그 보관소다.

## DeepSeek API 사용 (환경변수)

`03_apply`만 실제 API를 호출한다(01·02는 표준 라이브러리만). 키와 모델은 환경변수로 지정하며 코드·저장소에 직접 적지 않는다.

방법 1. `.env` 파일 (권장): 프로젝트 루트에서 `cp .env.example .env` 후 키를 적는다. `03_apply` 실행 시 상위 루트의 `.env`도 자동으로 읽는다.

방법 2. 셸 환경변수: `export DEEPSEEK_API_KEY="발급받은_키"`. 이미 설정된 환경변수는 `.env`보다 우선한다.

| 환경변수 | 필수 | 기본값 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | 03 실행 시 필수 | 없음 (없으면 status=error) |
| `DEEPSEEK_MODEL` | 선택 | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | 선택 | `https://api.deepseek.com` |
