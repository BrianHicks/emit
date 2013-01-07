'simple celery app'
from celery import Celery
from emit import Router

import logging

app = Celery(
    'celery_emit_example',
    broker='redis://'
)
app.conf.update(
    CELERY_IMPORTS = ('tasks',)
)

router = Router(celery_task=app.task, imports=['tasks'])

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
