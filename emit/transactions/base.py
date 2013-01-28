class TransactionHandler(object):
    def __init__(self):
        self.rollback_functions = {}

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
