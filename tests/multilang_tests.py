'tests for multilang'
from unittest import TestCase

import msgpack

from emit.router import Router
from emit.multilang import MultiLangNode

class SampleNode(MultiLangNode):
    command = 'python examples/multilang/test.py'


class SampleRubyNode(MultiLangNode):
    command = 'ruby examples/multilang/test.rb'


class MultiLangNodeTests(TestCase):
    'tests for MultiLangNode'
    def setUp(self):
        self.raw = SampleNode()
        self.node = Router().node(['n'])(self.raw)

    def test_deserialization(self):
        'serialization takes a Message and outputs msgpack'
        obj = {'x': 1, 'y': 2}
        packed = msgpack.packb(obj)

        self.assertEqual(
            obj,
            self.raw.deserialize(packed)
        )

    def test_get_command(self):
        'get_command gets command'
        node = SampleNode()

        self.assertEqual(
            ['python', 'examples/multilang/test.py'],
            self.raw.get_command()
        )

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
