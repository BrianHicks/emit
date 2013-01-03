'simple celery app'
from celery import Celery
from emit import Router

app = Celery(
    'celery_emit_example',
    broker='redis://'
)
app.conf.update(
    CELERY_IMPORTS = ('tasks',)
)
router = Router()
