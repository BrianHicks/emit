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
        self.router.transaction('test')(
            self.router.node(('x',))(self.func)
        )
        self.assertEqual(
            set([__name__ + '.test_func']),
            self.router.transactions['test']
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
            transaction_handler=TransactionHandler
        )

    def test_add_transaction(self):
        'add_transaction adds to a set'
        self.router.add_transaction('test', 'name')

        self.assertEqual(
            set(['name']),
            self.router.transactions['test']
        )

    def test_existing_transaction(self):
        'add_transaction uses existing set'
        self.router.transactions['test'] = set(['existing'])
        self.router.add_transaction('test', 'name')

        self.assertEqual(
            set(['existing', 'name']),
            self.router.transactions['test']
        )

    def test_return_value(self):
        'add_transaction returns new value'
        self.assertEqual(
            set(['name']),
            self.router.add_transaction('test', 'name')
        )


class AddRollbackFunctionTests(TestCase):
    'tests for Router.add_rollback_function'
    def setUp(self):
        self.router = Router(
            transaction_handler=TransactionHandler
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
