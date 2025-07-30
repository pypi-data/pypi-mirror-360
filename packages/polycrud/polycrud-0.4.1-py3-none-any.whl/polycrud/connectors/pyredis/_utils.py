from typing import Any
from urllib.parse import unquote, urlparse


def _parse_redis_url(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    username = unquote(parsed.username) if parsed.username else None
    password = unquote(parsed.password) if parsed.password else None
    db = int(parsed.path.strip("/")) if parsed.path.strip("/") else 0

    host_part = url.split("@")[-1].split("/")[0] if "@" in url else parsed.netloc.split("/")[0]
    hosts = [(h.strip().split(":")[0], int(h.strip().split(":")[1]) if ":" in h else 6379) for h in host_part.split(",")]

    return {"username": username, "password": password, "hosts": hosts, "db": db}
