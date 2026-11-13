from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "crm",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-overdue-tasks": {
            "task": "app.tasks.check_overdue_tasks",
            "schedule": 3600.0,
        },
    },
)
