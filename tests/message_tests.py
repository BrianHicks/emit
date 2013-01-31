'tests for message'
import json
from unittest import TestCase

from emit.messages import Message


class MessageTests(TestCase):
    'tests for Message'
    def test_dot_access(self):
        'accessing attributes'
        x = Message(x=1)
        self.assertEqual(1, x.x)

    def test_access_missing(self):
        'accessing attributes that do not exist'
        x = Message(x=1)
        try:
            self.assertRaisesRegex(
                AttributeError, '"y" is not included in this message',
                getattr, x, 'y'
            )
        except AttributeError:  # python 2.6
            self.assertRaises(
                AttributeError,
                getattr, x, 'y'
            )

    def test_repr(self):
        x = Message(x=1, y=2)
        try:
            self.assertRegexpMatches(
                repr(x),
                r'Message\(((x=1|y=2)(, )?){2}\)'
            )
        except AttributeError:  # python 2.6
            self.assertEqual(
                'Message(y=2, x=1)',
                repr(x)
            )

    def test_dir(self):
        'dir includes attributes'
        x = Message(x=1, y=2)
        try:
            self.assertIn('x', dir(x))
            self.assertIn('y', dir(x))
        except AttributeError:  # python 2.6
            self.assertTrue('x' in dir(x), '"x" not in dir(x)')
            self.assertTrue('y' in dir(x), '"y" not in dir(x)')

    def test_as_dict(self):
        'returns dict from .as_dict'
        x = Message(x=1, y=2)
        self.assertEqual(
            {'x': 1, 'y': 2},
            x.as_dict()
        )

    def test_as_json(self):
        'returns string from .as_msgpack'
        d = {'x': 1, 'y': 2}
        x = Message(**d)

        self.assertEqual(
            json.dumps(d),
            x.as_json()
        )

    def test_equality(self):
        'two messages are equal if their bundles are equal'
        d = {'x': 1, 'y': 2}
        x = Message(**d)
        y = Message(**d)

        self.assertEqual(x, y)
