class BaseTransactionHandler(object):
    'base transaction handler'
    def __init__(self):
        self.transactions = {}
        self.rollback_functions = {}

    def add_transaction(self, transaction_name, name):
        'add a transaction to transactions'
        transaction_names = self.transactions.setdefault(name, set())
        transaction_names.add(transaction_name)
        return transaction_names

    def add_rollback(self, transaction_name, name, rollback):
        'add a rollback function'
        raise NotImplementedError

    def set_transaction_id(self, message):
        'set a transaction ID'
        raise NotImplementedError

    def start_call(self, transaction_id, name, message):
        'start a transactional call'
        raise NotImplementedError

    def finish_call(self, transaction_id, name):
        'finish a call'
        raise NotImplementedError

    def rollback(self, transaction_id, name):
        'roll back a transaction'
        raise NotImplementedError
