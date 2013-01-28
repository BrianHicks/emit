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
