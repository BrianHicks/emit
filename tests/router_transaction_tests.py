'tests for transactions in the router'
from unittest import TestCase

from emit import Router


class MetaTests(TestCase):
    'tests for things outside of the actual transaction handling'
    def setUp(self):
        self.router = Router()

    def test_only_works_on_nodes(self):
        'transaction decorator only works on nodes'
        def func(msg):
            return msg.x

        transaction = self.router.transaction('test')
        try:
            self.assertRaisesRegexp(
                ValueError, 'transactions may only be applied to nodes',
                transaction, func
            )
        except AttributeError:  # python 2.6
            self.assertRaises(
                ValueError,
                transaction, func
            )
