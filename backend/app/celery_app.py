from celery import Celery
from .config import settings

celery = Celery(
    "demo",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

@celery.task
def optimize_image(attachment_id: int):
    return {"status": "ok", "attachment_id": attachment_id}

