'simple celery app'
from celery import Celery
from emit import CeleryRouter

app = Celery(
    'celery_emit_example',
    broker='redis://'
)
app.conf.update(
    CELERY_IMPORTS=('tasks',)
)

router = CeleryRouter(celery_task=app.task, node_modules=['tasks'])
