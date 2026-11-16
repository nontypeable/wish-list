import os
from http import HTTPStatus
from urllib.error import URLError
from urllib.request import Request, urlopen

host = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")[0].strip()
request = Request(
    "http://127.0.0.1:8000/healthz/",
    headers={"Host": host, "X-Forwarded-Proto": "https"},
)
try:
    with urlopen(request, timeout=3) as response:  # noqa: S310 — fixed loopback URL
        raise SystemExit(0 if response.status == HTTPStatus.OK and response.read() == b"ok" else 1)
except URLError, TimeoutError:
    raise SystemExit(1) from None
