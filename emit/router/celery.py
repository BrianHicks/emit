from __future__ import absolute_import

from .core import Router


class CeleryRouter(Router):
    'Router specifically for Celery routing'
    def __init__(self, celery_task, *args, **kwargs):
        '''\
        Specifically route when celery is needed

        :param celery_task: celery task to apply to all nodes (can be
                            overridden in :py:meth:`Router.node`.)
        :type celery_task: A celery task decorator, in any form
        '''
        super(CeleryRouter, self).__init__(*args, **kwargs)
        self.celery_task = celery_task
        self.logger.debug('Initialized Celery Router')

    def dispatch(self, origin, destination, message):
        '''\
        enqueue a message with Celery

        :param destination: destination to dispatch to
        :type destination: :py:class:`str`
        :param message: message to dispatch
        :type message: :py:class:`emit.message.Message` or subclass
        '''
        func = self.functions[destination]
        self.logger.debug('delaying %r', func)
        return func.delay(_origin=origin, **message)

    def wrap_node(self, node, options):
        '''\
        celery registers tasks by decorating them, and so do we, so the user
        can pass a celery task and we'll wrap our code with theirs in a nice
        package celery can execute.
        '''
        if 'celery_task' in options:
            return options['celery_task'](node)

        return self.celery_task(node)
