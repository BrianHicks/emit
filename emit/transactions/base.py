class TransactionHandler(object):
    def __init__(self):
        self.rollback_functions = {}

    def add_transaction(self, transaction_name, name):
        'add a transaction to transactions'
        raise NotImplementedError

    def add_rollback(self, transaction_name, name, rollback):
        'add a rollback function'
        raise NotImplementedError

    def set_transaction_id(self, message):
        'set a transaction ID'
        raise NotImplementedError

    def start_call(self, transaction, name, message):
        'start a transactional call'
        raise NotImplementedError

    def finish_call(self, transaction, name):
        'finish a call'
        raise NotImplementedError

    def rollback(self, transaction, name):
        'roll back a transaction'
        raise NotImplementedError
