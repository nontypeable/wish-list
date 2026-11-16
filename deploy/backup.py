"""Write a SQLite snapshot and uploaded media as a tar.gz to stdout."""

import os
import sqlite3
import sys
import tarfile
import tempfile
from contextlib import closing
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wish_list_config.settings")
# Script is invoked as `python deploy/backup.py` from /app.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import django
from django.conf import settings

django.setup()

database = Path(str(settings.DATABASES["default"]["NAME"]))
if not database.is_file():
    raise SystemExit("Database not found; run migrations before making a backup.")

with tempfile.TemporaryDirectory() as directory:
    snapshot = Path(directory) / "db.sqlite3"
    with (
        closing(sqlite3.connect(f"file:{database}?mode=ro", uri=True)) as source,
        closing(sqlite3.connect(snapshot)) as destination,
    ):
        source.backup(destination)
    with tarfile.open(fileobj=sys.stdout.buffer, mode="w|gz") as archive:
        archive.add(snapshot, arcname="data/db.sqlite3")
        media = Path(settings.MEDIA_ROOT)
        if media.is_dir():
            archive.add(media, arcname="media")
