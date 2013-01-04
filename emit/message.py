'message wrapper to be passed to functions'
import msgpack

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

    def __repr__(self):
        'representation of this message'
        return 'Message(%s)' % (
            ', '.join('%s=%s' % pair for pair in self.bundle.items())
        )

    def as_dict(self):
        '''\
        representation of this message as a dictionary

        :returns: dict
        '''
        return self.bundle

    def as_msgpack(self):
        '''
        representation of this message as a msgpack object

        :returns: str
        '''
        return msgpack.packb(self.as_dict())
