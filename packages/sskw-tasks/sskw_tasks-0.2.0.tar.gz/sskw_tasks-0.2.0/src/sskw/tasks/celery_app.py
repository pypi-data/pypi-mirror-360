from celery import Celery
import os

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

app = Celery(
    'sskw_tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['tasks'],
    timezone='UTC',
    enable_utc=True,
)

# 自动发现任务
app.autodiscover_tasks(['sskw.tasks'])