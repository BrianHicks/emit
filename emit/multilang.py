'class to communicate with other languages over stdin/out'
import logging
import msgpack
import shlex
from subprocess import Popen, PIPE


class MultiLangNode(object):
    '''\
    callable object to wrap communication to a node in another language

    to use this, subclass ``MultiLangNode``, providing "command". Decorate it
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
            stdout=PIPE, stderr=PIPE, stdin=PIPE
        )

        stdout, stderr = process.communicate(msg.as_msgpack())

        if stderr != '':
            self.logger.error('Error calling "%s": %s', self.command, stderr)
            raise RuntimeError(stderr)

        messages = stdout.strip().split('\n')
        for message in messages:
            yield self.deserialize(message)

    def get_command(self):
        'get the command as a list'
        return shlex.split(self.command)

    def deserialize(self, msg):
        'deserialize output to a Python object'
        self.logger.debug('deserializing %s', msg)
        return msgpack.unpackb(msg)
