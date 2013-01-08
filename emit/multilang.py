'class to communicate with other languages over stdin/out'
import logging
try:
    import msgpack
except ImportError:
    import msgpack_pure as msgpack
import shlex
from subprocess import Popen, PIPE


class ShellNode(object):
    '''\
    callable object to wrap communication to a node in another language

    to use this, subclass ``ShellNode``, providing "command". Decorate it
    however you feel like.

    Messages will be passed in on lines in msgpack format. This class expects
    similar output: msgpack messages separated by a newline.
    '''
    def __init__(self):
        self.logger = logging.getLogger('%s.%s' %(
            self.__class__.__module__,
            self.__class__.__name__
        ))
        self.logger.debug('initialized %s', self.__class__.__name__)

    @property
    def __name__(self):
        'fix for being able to use functools.wraps on a class'
        return self.__class__.__name__

    def __call__(self, msg):
        'call the command specified, processing output'
        process = Popen(
            self.get_command(),
            stdout=PIPE, stderr=PIPE, stdin=PIPE,
            cwd=self.get_cwd()
        )

        stdout, stderr = process.communicate(msg.as_msgpack())

        if stderr != '':
            self.logger.error('Error calling "%s": %s', self.command, stderr)
            raise RuntimeError(stderr)

        messages = stdout.strip().split('\n')
        self.logger.debug('subprocess returned %d messages', len(messages))
        for message in messages:
            yield self.deserialize(message)

    def get_command(self):
        'get the command as a list'
        return shlex.split(self.command)

    def get_cwd(self):
        'get directory to change to before running the command'
        try:
            return self.cwd
        except AttributeError:
            self.logger.debug('no cwd specified, returning None')
            return None

    def deserialize(self, msg):
        'deserialize output to a Python object'
        self.logger.debug('deserializing %s', msg)
        return msgpack.unpackb(msg)
