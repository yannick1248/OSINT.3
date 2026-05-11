from __future__ import annotations

import os

from celery import Celery

celery_app = Celery(
    "osintomega",
    broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
)

celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])
