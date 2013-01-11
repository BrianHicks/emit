'tests for emit/router.py'
from __future__ import print_function
from unittest import TestCase

from celery import Celery, Task
import mock

from emit.router import Router, CeleryRouter
from emit.message import Message, NoResult

def get_test_celery():
    celery = Celery()
    celery.conf.update(
        CELERY_ALWAYS_EAGER=True
    )
    return celery

def get_named_mock(name):
    m = mock.MagicMock()
    m.__name__ = name
    m.name = name
    return m

def prefix(name):
    return '%s.%s' % (__name__, name)


class RouterTests(TestCase):
    def setUp(self):
        self.router = Router()

    # node
    def test_node_adds_routes(self):
        'router adds routes for node when decorating'
        a = lambda x: x
        a.__name__ = 'a'

        b = lambda x: x
        b.__name__ = 'b'

        fields = ('field_a', 'field_b')
        self.router.node(fields)(a)
        self.router.node(fields, prefix('a'))(b)

        self.assertEqual(
            {prefix('a'): set([prefix('b')])},
            self.router.routes
        )

    def test_node_adds_fields(self):
        'router adds fields when decorating'
        a = lambda x: x
        a.__name__ = 'a'

        self.router.node(['a', 'b', 'c'])(a)

        self.assertEqual(
            ['a', 'b', 'c'],
            self.router.fields[prefix('a')]
        )

    # calling
    def test_calling_returns_single(self):
        'calling a function that returns explicitly wraps the value'

        @self.router.node(['sum', 'x', 'y'])
        def add(msg):
            return msg.x + msg.y, msg.x, msg.y

        self.assertEqual(
            {'sum': 3, 'x': 1, 'y': 2},
            add(x=1, y=2)
        )

    def test_calling_returns_multiple(self):
        'calling a function that yields returns multiple results'
        @self.router.node(['combination'])
        def suffixes(msg):
            for suf in msg.sufs:
                yield msg.pre + suf

        self.assertEqual(
            (
                {'combination': 'stuffy'},
                {'combination': 'stuffier'},
                {'combination': 'stuffiest'}
            ),
            suffixes(pre='stuff', sufs=['y', 'ier', 'iest'])
        )

    def test_routing(self):
        'calling a function will route to subscribed functions'
        n = 5

        squares = [i*i for i in range(n)]
        returned_squares = []

        doubles = [i*2 for i in range(n)]
        returned_doubles = []

        @self.router.node(['i'])
        def yield_n(msg):
            for i in range(msg.to):
                yield i

        @self.router.node(['squared'], [prefix('yield_n')])
        def square(msg):
            returned_squares.append(msg.i ** 2)
            return msg.i ** 2

        @self.router.node(['doubled'], [prefix('yield_n')])
        def double(msg):
            returned_doubles.append(msg.i * 2)
            return msg.i * 2

        yield_n(to=n)

        self.assertEqual(doubles, returned_doubles)
        self.assertEqual(squares, returned_squares)

    def test_get_name(self):
        'get name gets the __name__ property by default'
        l = lambda x: x
        l.__name__ = 'test'

        self.assertEqual(
            prefix('test'),
            self.router.get_name(l)
        )

    def test_get_name_celery(self):
        'gets the name of a celery-decorated function'
        celery = get_test_celery()
        l = lambda x: x
        l.__name__ = 'test'
        l = celery.task(l)

        self.assertEqual(prefix('test'), self.router.get_name(l))

    def test_custom_message(self):
        'sends a custom message type'
        class CMessage(Message):
            pass

        r = Router(message_class=CMessage)

        @r.node(['x'])
        def test(x):
            self.assertTrue(isinstance(x, CMessage))

        test(x=1)

    def test_initial(self):
        'registering a function with initial calls it from calling the router'
        @self.router.node(['x'], entry_point=True)
        def test(msg):
            raise RuntimeError('test was called')

        try:
            self.assertRaisesRegexp(
                RuntimeError, 'test was called',
                self.router, x=1
            )
        except AttributeError:  # python 2.6
           self.assertRaises(RuntimeError, self.router, x=1)


    @mock.patch('emit.router.importlib')
    def test_registers_node_modules(self, mock_importlib):
        'register node modules in init (instead of importing right away)'
        r = Router(node_modules=['test'], node_package='test')

        self.assertEqual(['test'], r.node_modules)
        self.assertEqual('test', r.node_package)
        self.assertEqual(False, r.resolved_node_modules)
        self.assertEqual(0, mock_importlib.import_module.call_count)

    @mock.patch('emit.router.importlib')
    def test_imports_with_resolve_node_modules(self, mock_importlib):
        'resolves imports'
        r = Router(node_modules=['test'], node_package='test')
        r.resolve_node_modules()

        mock_importlib.import_module.assert_called_with('test', 'test')

    @mock.patch('emit.router.importlib')
    def test_imports_only_once(self, mock_importlib):
        'resolves imports only once'
        r = Router(node_modules=['test'], node_package='test')

        # twice!
        r.resolve_node_modules()
        r.resolve_node_modules()

        self.assertEqual(1, mock_importlib.import_module.call_count)

    def test_no_result_generator(self):
        'a generator returning NoResult should only pass on non-NoResults'
        @self.router.node(['n'])
        def n_generator(msg):
            for n in range(msg.n):
                yield n if n % 2 == 0 else NoResult

        watcher = get_named_mock('watcher')
        self.router.node(['n'], prefix('n_generator'))(watcher)

        n_generator(n=6)

        self.assertEqual(3, watcher.call_count)

    def test_no_result_single(self):
        'a function returning NoResult should only pass on non-NoResults'
        func = lambda msg: NoResult
        func.__name__ = 'func'
        func = self.router.node(['n'])(func)

        watcher = get_named_mock('watcher')
        self.router.node(['n'], 'func')(watcher)

        func(n=1)

        self.assertEqual(0, watcher.call_count)

    def test_register_route_regex(self):
        'adding routes with a regular expression route correctly'
        self.router.register_route('__entry_point', 'test')
        self.router.register_route('.+', 'test2')

        self.assertEqual(
            {'test': set(['test2'])},
            self.router.routes
        )

    def test_register_route_before(self):
        'adding routes after a regex has been added also match'
        self.router.register_route('.+', 'test2')
        self.router.register_route('__entry_point', 'test')

        self.assertEqual(
            {'test': set(['test2'])},
            self.router.routes
        )

    def test_unsubscribed_routes_are_added(self):
        'routes which have no subscribers are still added later'
        self.router.register_route('.+', 'test2')
        self.router.register_route(None, 'test')

        self.assertEqual(
            {'test': set(['test2'])},
            self.router.routes
        )

    def test_ignored_routes(self):
        'ignored routes are not added'
        # add two base routes
        self.router.register_route(None, 'test1')
        self.router.register_route(None, 'test2')

        # add ignore route
        self.router.register_route(['test1', 'test2'], 'test3')
        self.router.register_ignore('test2', 'test3')

        self.assertEqual(
            {'test1': set(['test3'])},
            self.router.routes
        )

class CeleryRouterTests(TestCase):
    'tests for using celery to route nodes'
    def setUp(self):
        self.celery = get_test_celery()
        self.router = CeleryRouter(self.celery.task)

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
