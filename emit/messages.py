'message wrapper to be passed to functions'
import json


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
        return sorted(list(['bundle'] + list(self.bundle.keys())))

    def __repr__(self):
        'representation of this message'
        return 'Message(%s)' % (
            ', '.join('%s=%s' % pair for pair in self.bundle.items())
        )

    def __eq__(self, other):
        'test equality of two messages'
        return self.bundle == other.bundle

    def as_dict(self):
        '''\
        representation of this message as a dictionary

        :returns: dict
        '''
        return self.bundle

    def as_json(self):
        '''
        representation of this message as a json object

        :returns: str
        '''
        return json.dumps(self.as_dict())


class NoResult(object):
    'single value to return from a node to stop further processing'
    pass
