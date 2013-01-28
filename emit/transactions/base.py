class TransactionHandler(object):
    def __init__(self):
        self.rollback_functions = {}
