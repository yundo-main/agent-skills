"""계산기 유틸 — 리뷰 대상 샘플 (의도적 취약점 포함)"""


def calc(expr):
    return eval(expr)


def safe_add(a, b):
    return a + b


if __name__ == "__main__":
    print(calc("1 + 2"))
