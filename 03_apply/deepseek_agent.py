"""[공용] DeepSeek 백엔드 — 교체 가능한 에이전트 부품
역할: 부품 — OpenAI 호환 chat API를 호출한다. 실행은 main.py에서 한다
의존: 없음 (표준 라이브러리만 사용)
환경: DEEPSEEK_API_KEY(필수) · DEEPSEEK_MODEL · DEEPSEEK_BASE_URL

'*_agent' 계열 부품 규약: (user:str, system:str="") -> str.
apply.run_with_skill의 agent 인자로 주입되므로, 같은 시그니처를 갖는
다른 백엔드(openai_agent 등)로 그대로 교체할 수 있다.
"""

import json
import os
import urllib.request

DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com"  # OpenAI 호환 엔드포인트
TIMEOUT_SEC = 60


def load_dotenv(path=".env"):
    """루트 .env를 읽어 아직 없는 환경변수만 채운다.

    각 단계 디렉터리는 독립 프로젝트이므로 현재 디렉터리의 .env를 먼저 보고,
    없으면 상위(프로젝트 루트)의 .env를 찾는다.
    이미 설정된 셸 환경변수가 .env보다 우선한다(setdefault).
    키는 이 파일에만 — 코드·문서 어디에도 값을 적지 않는다.
    """
    for base in (path, os.path.join("..", path)):
        if os.path.isfile(base):
            path = base
            break
    if not os.path.isfile(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def deepseek_agent(user, system=""):
    """(user, system) -> str. 키 부재·API 오류는 예외로 올린다.

    호출부(run_with_skill)가 예외를 받아 status="error"로 변환하므로
    이 함수는 결과 텍스트만 돌려주고 에러 처리는 하지 않는다.
    """
    load_dotenv()
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY 없음 — .env 또는 환경변수로 설정")
    url = (os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
           + "/chat/completions")
    # 스킬 본문이 system으로 주입되는 자리 — 절차는 위(system), 작업물은 아래(user)
    body = {
        "model": os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL),
        "messages": ([{"role": "system", "content": system}] if system else [])
                    + [{"role": "user", "content": user}],
    }
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()
