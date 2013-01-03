'tests for emit/router.py'
from collections import namedtuple
from unittest import TestCase

from emit.router import Router

class RouterTests(TestCase):
    # node
    def test_node_adds_routes(self):
        'router adds routes for node when decorating'
        r = Router()
        a = lambda x: x
        a.func_name = 'a'

        b = lambda x: x
        b.func_name = 'b'

        fields = ('field_a', 'field_b')
        r.node(fields)(a)
        r.node(fields, 'a')(b)

        self.assertEqual({'a': set('b')}, r.routes)

    def test_node_adds_fields(self):
        'router adds fields when decorating'
        r = Router()
        a = lambda x: x
        a.func_name = 'a'

        r.node(['a', 'b', 'c'])(a)

        should = namedtuple('a_fields', ['a', 'b', 'c'])
        self.assertEqual(
            should._fields,
            r.fields['a']._fields
        )
        self.assertEqual(
            should.__name__,
            r.fields['a'].__name__
        )

    # add_routes
    def test_creates_new_route(self):
        'creates a new route from blank routes'
        r = Router()
        r.add_routes(['a', 'b'], 'c')

        self.assertEqual(set('c'), r.routes['a'])
        self.assertEqual(set('c'), r.routes['b'])

    def test_appends_existing_route(self):
        'appends a route to an existing route'
        r = Router({'a': set('b')})
        r.add_routes(['a'], 'c')

        self.assertEqual(set(['b', 'c']), r.routes['a'])

    def test_converts_origin(self):
        'converts a single origin to a list'
        r = Router()
        r.add_routes('a', 'bc')

        self.assertEqual(set(['bc']), r.routes['a'])

    # calling
    def test_calling_returns_single(self):
        'calling a function that returns explicitly wraps the value'
        r = Router()

        @r.node(['sum', 'x', 'y'])
        def add(x, y):
            return x + y, x, y

        self.assertEqual(
            r.fields['add'](3, 1, 2),
            add(1, 2)
        )

    def test_calling_returns_multiple(self):
        'calling a function that yields returns multiple results'
        r = Router()

        @r.node(['combination'])
        def suffixes(pre, sufs):
            for suf in sufs:
                yield pre + suf

        self.assertEqual(
            (
                r.fields['suffixes']('stuffy'),
                r.fields['suffixes']('stuffier'),
                r.fields['suffixes']('stuffiest'),
            ),
            suffixes('stuff', ['y', 'ier', 'iest'])
        )

    def test_routing(self):
        'calling a function will route to subscribed functions'
        r = Router()
        n = 5

        squares = [i*i for i in range(n)]
        returned_squares = []

        doubles = [i*2 for i in range(n)]
        returned_doubles = []

        @r.node(['i'])
        def yield_n(to):
            for i in range(to):
                yield i

        @r.node(['squared'], ['yield_n'])
        def square(msg):
            returned_squares.append(msg.i * msg.i)
            return msg.i * msg.i

        @r.node(['doubled'], ['yield_n'])
        def double(msg):
            returned_doubles.append(msg.i * 2)
            return msg.i * 2

        yield_n(n)
        self.assertEqual(doubles, returned_doubles)
        self.assertEqual(squares, returned_squares)

    def test_get_name(self):
        'get name gets the func_name property by default'
        r = Router()
        l = lambda x: x
        l.func_name = 'test'

        self.assertEqual('test', r.get_name(l))
