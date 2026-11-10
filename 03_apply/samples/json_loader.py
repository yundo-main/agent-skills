"""설정 로더 — 리뷰 대상 샘플 (의도적 오류 삼킴 포함)"""
import json


def load(raw):
    try:
        return json.loads(raw)
    except:
        pass


def load_or_default(raw):
    try:
        return json.loads(raw)
    except ValueError:
        return {}
