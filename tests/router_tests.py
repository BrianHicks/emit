'tests for emit/router.py'
from unittest import TestCase

from celery import Celery, Task

from emit.router import Router
from emit.message import Message

def get_test_celery():
    celery = Celery()
    celery.conf.update(
        CELERY_ALWAYS_EAGER=True
    )
    return celery

class RouterTests(TestCase):
    def setUp(self):
        self.router = Router()

    # node
    def test_node_adds_routes(self):
        'router adds routes for node when decorating'
        a = lambda x: x
        a.func_name = 'a'

        b = lambda x: x
        b.func_name = 'b'

        fields = ('field_a', 'field_b')
        self.router.node(fields)(a)
        self.router.node(fields, 'a')(b)

        self.assertEqual({'a': set('b')}, self.router.routes)

    def test_node_adds_fields(self):
        'router adds fields when decorating'
        a = lambda x: x
        a.func_name = 'a'

        self.router.node(['a', 'b', 'c'])(a)

        self.assertEqual(
            ['a', 'b', 'c'],
            self.router.fields['a']
        )

    # add_routes
    def test_creates_new_route(self):
        'creates a new route from blank routes'
        self.router.add_routes(['a', 'b'], 'c')

        self.assertEqual(set('c'), self.router.routes['a'])
        self.assertEqual(set('c'), self.router.routes['b'])

    def test_appends_existing_route(self):
        'appends a route to an existing route'
        r = Router({'a': set('b')})
        r.add_routes(['a'], 'c')

        self.assertEqual(set(['b', 'c']), r.routes['a'])

    def test_converts_origin(self):
        'converts a single origin to a list'
        self.router.add_routes('a', 'bc')

        self.assertEqual(set(['bc']), self.router.routes['a'])

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

        @self.router.node(['squared'], ['yield_n'])
        def square(msg):
            returned_squares.append(msg.i ** 2)
            return msg.i ** 2

        @self.router.node(['doubled'], ['yield_n'])
        def double(msg):
            returned_doubles.append(msg.i * 2)
            return msg.i * 2

        yield_n(to=n)
        self.assertEqual(doubles, returned_doubles)
        self.assertEqual(squares, returned_squares)

    def test_get_name(self):
        'get name gets the func_name property by default'
        l = lambda x: x
        l.func_name = 'test'

        self.assertEqual('test', self.router.get_name(l))

    def test_get_name_celery(self):
        'gets the name of a celery-decorated function'
        celery = get_test_celery()
        l = lambda x: x
        l.func_name = 'test'
        l = celery.task(l)

        self.assertEqual('tests.router_tests.test', self.router.get_name(l))

    def test_custom_message(self):
        'sends a custom message type'
        class CMessage(Message):
            pass

        r = Router(message_class=CMessage)

        @r.node(['x'])
        def test(x):
            self.assertTrue(isinstance(x, CMessage))

        test(x=1)

class CeleryRouterTests(TestCase):
    'tests for using celery to route nodes'
    def setUp(self):
        self.celery = get_test_celery()
        self.router = Router()

    def test_registers_as_task(self):
        'registers the function as a task'
        l = lambda x: x
        l.func_name = 'test'
        self.router.node(['test'], celery_task=self.celery.task)(l)

        self.assertTrue(
            isinstance(self.router.functions['tests.router_tests.test'], Task)
        )

    def test_adds_when_initialized(self):
        'if router is passed a celery task when initialized it wraps with it'
        r = Router(celery_task=self.celery.task)

        l = lambda x: x
        l.func_name = 'test'
        r.node(['test'])(l)

        self.assertTrue(
            isinstance(r.functions['tests.router_tests.test'], Task)
        )
