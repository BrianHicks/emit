'tests for emit/router.py'
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
