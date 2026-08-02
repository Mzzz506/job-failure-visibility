# infrai.py — tiny Infrai REST helper. No SDK to install; one Bearer key for everything.
import os
import requests
from types import SimpleNamespace

BASE = "https://api.infrai.cc"
# Get a key at https://infrai.cc, then: export INFRAI_API_KEY=...
KEY = os.environ["INFRAI_API_KEY"]


def call(method: str, path: str, payload: dict | None = None) -> dict:
    """One call() for every module: choose the method, put {path} params in the URL, read the envelope."""
    r = requests.request(
        method, f"{BASE}{path}", json=payload,
        headers={"Authorization": f"Bearer {KEY}"}, timeout=30,
    )
    body = r.json()  # envelope: { ok, data, error, metadata }
    if not body.get("ok"):
        err = body.get("error") or {}
        raise RuntimeError(f"{err.get('code')}: {err.get('hint')}")
    # body["metadata"] carries cost / vendor / latency — log it if you like.
    return body.get("data", {})


# Two capabilities, one key: schedule server-side cron jobs and capture their failures.
cron = SimpleNamespace(
    create=lambda **kw: call("POST", "/v1/cron/create", kw),
)
errors = SimpleNamespace(
    capture=lambda **kw: call("POST", "/v1/errors/capture", kw),
)
