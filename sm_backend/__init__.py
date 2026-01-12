# Import Celery app to ensure tasks are discovered when Django starts
from .celery import app as celery_app

__all__ = ('celery_app',)
