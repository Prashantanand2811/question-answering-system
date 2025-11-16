# app/client.py
import httpx
from functools import lru_cache

BASE = "http://november7-730026606190.europe-west1.run.app"  # http, not https

@lru_cache(maxsize=1)
def get_messages():
    r = httpx.get(f"{BASE}/messages/", timeout=10,follow_redirects=True)  # trailing slash
    r.raise_for_status()
    data = r.json()
    items = data["items"] if isinstance(data, dict) and "items" in data else data
    items.sort(key=lambda m: m.get("timestamp",""), reverse=True)
    return items

def known_names():
    return sorted({m["user_name"] for m in get_messages() if m.get("user_name")})
