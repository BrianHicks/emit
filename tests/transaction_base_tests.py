'tests for Base transaction handler'
from unittest import TestCase

from emit import Router
from emit.transactions.base import BaseTransactionHandler


def test_notimplemented():
    'test methods which have to be implemented by subclasses'
    methods = [
        ('start_call', ('transaction_name', 'name', 'message')),
        ('finish_call', ('transaction', 'name')),
        ('rollback', ('transaction', 'name')),
    ]
    for method, args in methods:
        yield single_notimplemented, method, args


def single_notimplemented(method, args):
    'test a single notimplemented'
    try:
        getattr(BaseTransactionHandler(), method)(*args)
        assert False, 'NotImplementedError not raised'
    except NotImplementedError:
        pass


class AddTransactionTests(TestCase):
    'tests for BaseTransactionHandler.add_transaction'
    def setUp(self):
        self.handler = BaseTransactionHandler()

    def test_new(self):
        'creates and adds to a set'
        self.handler.add_transaction('trans_name', 'func_name')

        self.assertEqual(
            set(['trans_name']),
            self.handler.transactions['func_name']
        )

    def test_existing(self):
        'adds to a set'
        self.handler.transactions['func_name'] = set(['test'])
        self.handler.add_transaction('trans_name', 'func_name')

        self.assertEqual(
            set(['trans_name', 'test']),
            self.handler.transactions['func_name']
        )

    def test_returns(self):
        'returns new value'
        self.assertEqual(
            set(['trans_name']),
            self.handler.add_transaction('trans_name', 'func_name')
        )


class AddRollbackTests(TestCase):
    'test for BaseTransactionHandler.add_rollback'
    def setUp(self):
        self.handler = BaseTransactionHandler()
        self.func = lambda x: x
