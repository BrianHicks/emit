'tests for transactions in the router'
from unittest import TestCase

from emit import Router
from emit.message import Message
from emit.transactions.base import BaseTransactionHandler


class RouterTransactionTests(TestCase):
    'tests for things outside of the actual transaction handling'
    def setUp(self):
        self.router = Router(
            transaction_handler=BaseTransactionHandler()
        )

        self.func = lambda msg: msg.x
        self.func.__name__ = 'test_func'

        self.rollback = lambda msg: msg.x

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

    def test_adds_to_transaction(self):
        'transaction adds the name to transactions'
        self.router.transaction('test_transaction')(
            self.router.node(('x',))(self.func)
        )
        self.assertEqual(
            set(['test_transaction']),
            self.router.transactions[__name__ + '.test_func']
        )

    def test_adds_rollback_function(self):
        'transaction adds rollback function'
        self.router.transaction('test', self.rollback)(
            self.router.node(('x',))(self.func)
        )
        self.assertEqual(
            {__name__ + '.test_func': self.rollback},
            self.router.rollback_functions['test']
        )


class AddToTransactionTests(TestCase):
    'tests for add_transaction'
    def setUp(self):
        self.router = Router(
            transaction_handler=BaseTransactionHandler()
        )

    def test_add_transaction(self):
        'add_transaction adds to a set'
        self.router.add_transaction('test_transaction', 'name')

        self.assertEqual(
            set(['test_transaction']),
            self.router.transactions['name']
        )

    def test_existing_transaction(self):
        'add_transaction uses existing set'
        self.router.transactions['name'] = set(['existing_transaction'])
        self.router.add_transaction('test_transaction', 'name')

        self.assertEqual(
            set(['existing_transaction', 'test_transaction']),
            self.router.transactions['name']
        )

    def test_return_value(self):
        'add_transaction returns new value'
        self.assertEqual(
            set(['test_transaction']),
            self.router.add_transaction('test_transaction', 'name')
        )


class AddRollbackFunctionTests(TestCase):
    'tests for Router.add_rollback_function'
    def setUp(self):
        self.router = Router(
            transaction_handler=BaseTransactionHandler()
        )
        self.func = lambda x: x

    def test_adds_new(self):
        'adds new rollback function'
        self.router.add_rollback_function(
            'test', 'name', self.func
        )
        self.assertEqual(
            {'name': self.func},
            self.router.rollback_functions['test']
        )

    def test_uses_existing(self):
        'uses existing rollback dict'
        self.router.rollback_functions = {
            'test': {'test': self.func}
        }
        self.router.add_rollback_function(
            'test', 'name', self.func
        )
        self.assertEqual(
            {
                'name': self.func,
                'test': self.func,
            },
            self.router.rollback_functions['test']
        )

    def test_return_value(self):
        'returns modified value'
        self.assertEqual(
            {'name': self.func},
            self.router.add_rollback_function(
                'test', 'name', self.func
            )
        )


class SetTransactionIdTests(TestCase):
    'tests for Router.set_transaction_id'
    def setUp(self):
        self.router = Router(
            transaction_handler=BaseTransactionHandler()
        )

    def test_new(self):
        'sets a new transaction ID'
        msg = Message({'a': 1})
        self.assertFalse(hasattr(msg, '_transaction'))

        msg, _id = self.router.set_transaction_id(msg)

        self.assertTrue(hasattr(msg, '_transaction'))

    def test_existing(self):
        'gets an existing transaction id'
        msg = Message({'a': 1, '_transaction': 'test'})

        new, _id = self.router.set_transaction_id(msg)
        self.assertEqual(msg, new)
        self.assertEqual('test', msg._transaction)
