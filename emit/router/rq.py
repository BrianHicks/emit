from __future__ import absolute_import
from rq import Queue
from rq.decorators import job

from .core import Router


class RQRouter(Router):
    'Router specifically for RQ routing'
    def __init__(self, redis_connection, *args, **kwargs):
        '''\
        Specific routing when using RQ

        :param redis_connection: a redis connection to send to all the tasks
                                 (can be overridden in :py:meth:`Router.node`.)
        :type redis_connection: :py:class:`redis.Redis`
        '''
        super(RQRouter, self).__init__(*args, **kwargs)
        self.redis_connection = redis_connection
        self.logger.debug('Initialized RQ Router')

    def dispatch(self, origin, destination, message):
        'dispatch through RQ'
        func = self.functions[destination]
        self.logger.debug('enqueueing %r', func)
        return func.delay(_origin=origin, **message)

    def wrap_node(self, node, options):
        '''
        we have the option to construct nodes here, so we can use different
        queues for nodes without having to have different queue objects.
        '''
        job_kwargs = {
            'queue': options.get('queue', 'default'),
            'connection': options.get('connection', self.redis_connection),
            'timeout': options.get('timeout', None),
            'result_ttl': options.get('result_ttl', 500),
        }

        return job(**job_kwargs)(node)
