import mock
from unittest import TestCase
from .utils import skipIf

from emit.router.celery import CeleryRouter

try:
    from celery import Celery, Task
except ValueError:  # Celery doesn't work under Python 3.3 - when it does it'll test again
    Celery = None


def prefix(name):
    return '%s.%s' % (__name__, name)


@skipIf(Celery is None, 'Celery did not import correctly')
class CeleryRouterTests(TestCase):
    'tests for using celery to route nodes'
    def setUp(self):
        self.celery = self.get_test_celery()
        self.router = CeleryRouter(self.celery.task)

    def get_test_celery(self):
        celery = Celery()
        celery.conf.update(
            CELERY_ALWAYS_EAGER=True
        )
        return celery

    def test_registers_as_task(self):
        'registers the function as a task'
        l = lambda x: x
        l.__name__ = 'test'
        self.router.node(['test'], celery_task=self.celery.task)(l)

        self.assertTrue(
            isinstance(self.router.functions[prefix('test')], Task)
        )

    def test_adds_when_initialized(self):
        'if router is passed a celery task when initialized it wraps with it'
        r = CeleryRouter(celery_task=self.celery.task)

        l = lambda x: x
        l.__name__ = 'test'
        r.node(['test'])(l)

        self.assertTrue(
            isinstance(r.functions[prefix('test')], Task)
        )

    def test_calls_delay(self):
        'calls delay to route'
        func = lambda n: n
        func.name = 'name'
        self.router.node(tuple(), entry_point=True)(func)

        node = mock.Mock()  # replace node with mock to test call
        self.router.functions['name'] = node

        self.router(x=1)

        node.delay.assert_called_with(_origin='__entry_point', x=1)

    def test_get_name_celery(self):
        'gets the name of a celery-decorated function'
        l = lambda x: x
        l.__name__ = 'test'
        l = self.celery.task(l)

        self.assertEqual(prefix('test'), self.router.get_name(l))
