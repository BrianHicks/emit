'message wrapper to be passed to functions'
class Message(object):
    'Convenient wrapper around a dictionary to provide attribute access'
    def __init__(self, *args, **kwargs):
        self.bundle = dict(*args, **kwargs)

    def __getattr__(self, attr):
        try:
            return self.bundle[attr]
        except KeyError:
            raise AttributeError(
                '"%s" is not included in this message' % attr
            )

    def __dir__(self):
        'get directory of attributes. include bundle.'
        return sorted(list(['bundle'] + self.bundle.keys()))
