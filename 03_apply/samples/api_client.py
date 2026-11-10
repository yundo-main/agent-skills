"""API 클라이언트 — 리뷰 대상 샘플 (의도적 하드코딩 키 포함)"""
import urllib.request

API_KEY = "sk-demo-not-a-real-key-0000"


def fetch(url):
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()
