'tests for message'
from unittest import TestCase

from emit.message import Message


class MessageTests(TestCase):
    'tests for Message'
    def test_dot_access(self):
        'accessing attributes'
        x = Message(x=1)
        self.assertEqual(1, x.x)

    def test_dir(self):
        'dir includes attributes'
        x = Message(x=1, y=2)
        self.assertIn('x', dir(x))
        self.assertIn('y', dir(x))

    def test_as_dict(self):
        'returns dict from .as_dict'
        x = Message(x=1, y=2)
        self.assertEqual(
            {'x': 1, 'y': 2},
            x.as_dict()
        )
