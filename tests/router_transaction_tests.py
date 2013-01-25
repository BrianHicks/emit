'tests for transactions in the router'
from unittest import TestCase

from emit import Router
from emit.transactions.base import TransactionHandler


class MetaTests(TestCase):
    'tests for things outside of the actual transaction handling'
    def setUp(self):
        self.router = Router(
            transaction_handler=TransactionHandler
        )

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

    def test_raises_if_no_handler(self):
        'transaction decorator only works if there is a handler'
        @self.router.node(('x',))
        def func(msg):
            return msg.x

        self.router.transaction_handler = None
        try:
            self.assertRaisesRegexp(
                ValueError, 'there is no transaction handler on the router',
                self.router.transaction, 'test'
            )
        except AttributeError:
            self.assertRaises(
                ValueError,
                self.router.transaction, 'test'
            )
