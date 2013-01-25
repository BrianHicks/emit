'tests for transactions in the router'
from unittest import TestCase

from emit import Router
from emit.transactions.base import TransactionHandler


class RouterTransactionTests(TestCase):
    'tests for things outside of the actual transaction handling'
    def setUp(self):
        self.router = Router(
            transaction_handler=TransactionHandler
        )

        self.func = lambda msg: msg.x

    def test_only_works_on_nodes(self):
        'transaction decorator only works on nodes'
        transaction = self.router.transaction('test')
        try:
            self.assertRaisesRegexp(
                ValueError, 'transactions may only be applied to nodes',
                transaction, self.func
            )
        except AttributeError:  # python 2.6
            self.assertRaises(
                ValueError,
                transaction, self.func
            )

    def test_raises_if_no_handler(self):
        'transaction decorator only works if there is a handler'
        func = self.router.node(('x',))(self.func)

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


class AddToTransactionTests(TestCase):
    'tests for add_to_transaction'
    def setUp(self):
        self.router = Router(
            transaction_handler=TransactionHandler
        )

    def test_add_transaction(self):
        'add_transaction adds to a set'
        self.assertEqual(
            set(['name']),
            self.router.add_to_transaction('test', 'name')
        )

    def test_existing_transaction(self):
        'add_transaction uses existing set'
        self.router.transactions['test'] = set(['existing'])
        self.assertEqual(
            set(['existing', 'name']),
            self.router.add_to_transaction('test', 'name')
        )
