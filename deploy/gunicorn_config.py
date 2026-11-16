import os
import tempfile

bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS", "1"))
worker_class = "gthread"
threads = int(os.environ.get("GUNICORN_THREADS", "2"))
timeout = 60
graceful_timeout = 30
keepalive = 5
worker_tmp_dir = tempfile.gettempdir()
umask = 0o022
# The web port is not published; only our Caddy proxy can reach it externally.
forwarded_allow_ips = "*"
accesslog = "-"
errorlog = "-"
# Invitation codes are secrets: don't put URL paths or query strings in access logs.
access_log_format = "%(h)s %(m)s %(s)s %(b)s %(L)s"
