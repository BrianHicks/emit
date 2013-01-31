'tests for multilang'
import json
from unittest import TestCase

from emit.router.core import Router
from emit.multilang import ShellNode


class SampleNode(ShellNode):
    command = 'python test.py'
    cwd = 'examples/multilang'


class SampleRubyNode(ShellNode):
    command = 'bundle exec ruby test.rb'
    cwd = 'examples/multilang'


class ShellNodeTests(TestCase):
    'tests for ShellNode'
    def setUp(self):
        self.raw = SampleNode()
        self.node = Router().node(['n'])(self.raw)

    def test_deserialization(self):
        'serialization takes a Message and outputs json'
        obj = {'x': 1, 'y': 2}
        packed = json.dumps(obj)

        self.assertEqual(
            obj,
            self.raw.deserialize(packed)
        )

    def test_get_command(self):
        'get_command gets command'
        self.assertEqual(
            ['python', 'test.py'],
            self.raw.get_command()
        )

    def test_get_cwd(self):
        'get_cwd gets cwd'
        self.assertEqual(
            'examples/multilang',
            self.raw.get_cwd()
        )

    def test_get_cwd_none(self):
        'get_cwd gets None if cwd is undefined'
        class NoCwd(ShellNode):
            command = 'x'

        raw = NoCwd()

        self.assertEqual(None, raw.get_cwd())

    def test_runs(self):
        'running returns proper output'
        self.assertEqual(
            (
                {'n': 0},
                {'n': 1},
                {'n': 2},
                {'n': 3},
                {'n': 4}
            ),
            self.node(count=5)
        )

    def test_runs_ruby(self):
        'running ruby example works'
        r = Router()
        rb_node = r.node(['n'])(SampleRubyNode())

        self.assertEqual(
            (
                {'n': 0},
                {'n': 1},
                {'n': 2},
                {'n': 3},
                {'n': 4}
            ),
            rb_node(count=5)
        )
