import os
from celery import Celery

celery_app = Celery(
    "sellerdash",
    broker=os.environ["REDIS_URL"],
    backend=os.environ["REDIS_URL"],
)

celery_app.conf.task_routes = {
    "tasks.*": {"queue": "default"}
}