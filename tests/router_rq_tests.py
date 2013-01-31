import mock
from redis import Redis
from unittest import TestCase

from .utils import skipIf

try:
    import rq
    from emit.router.rq import RQRouter
except ImportError:
    RQRouter = None


@skipIf(RQRouter is None, 'RQ did not import correctly')
class RQRouterTests(TestCase):
    'tests for using RQ to route nodes'
    def setUp(self):
        self.redis = Redis()
        self.router = RQRouter(self.redis)

        self.func = lambda n: n
        self.func.__name__ = 'test_function'

    def test_dispatches_with_delay(self):
        'dispatches by calling delay'
        node = mock.Mock()
        self.router.functions['test'] = node

        self.router.dispatch('origin', 'test', {'x': 1})

        node.delay.assert_called_with(_origin='origin', x=1)

    @mock.patch('emit.router.rq.job')
    def test_registers_as_job(self, fake_job):
        'registers the task with the job decorator'
        self.router.node(tuple())(self.func)

        decorator = fake_job()
        self.assertEqual(1, decorator.call_count)

    @mock.patch('emit.router.rq.job')
    def test_accepts_queue(self, fake_job):
        'accepts queue'
        self.router.node(tuple(), queue='test')(self.func)

        fake_job.assert_called_with(
            queue='test', connection=self.redis,
            timeout=None, result_ttl=500
        )

    @mock.patch('emit.router.rq.job')
    def test_accepts_connection(self, fake_job):
        'accepts connection'
        redis = Redis()
        self.router.node(tuple(), connection=redis)(self.func)

        fake_job.assert_called_with(
            queue='default', connection=redis,
            timeout=None, result_ttl=500
        )

    @mock.patch('emit.router.rq.job')
    def test_accepts_timeout(self, fake_job):
        'accepts timeout'
        self.router.node(tuple(), timeout=30)(self.func)

        fake_job.assert_called_with(
            queue='default', connection=self.redis,
            timeout=30, result_ttl=500
        )

    @mock.patch('emit.router.rq.job')
    def test_accepts_result_ttl(self, fake_job):
        'accepts result_ttl'
        self.router.node(tuple(), result_ttl=30)(self.func)

        fake_job.assert_called_with(
            queue='default', connection=self.redis,
            timeout=None, result_ttl=30
        )
