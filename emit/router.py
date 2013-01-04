'router for emit'
from functools import wraps
from types import GeneratorType

import logging

from .message import Message

class Router(object):
    'A router object. Holds routes and references to functions for dispatch'
    def __init__(self, initial_routes=None, celery_task=None, message_class=None):
        '''\
        Create a new router object. All parameters are optional.

        :param initial_routes: custom routes to initiate router with
        :type initial_routes: dict
        :param celery_task: celery task to apply to all nodes (can be
                            overridden in :py:meth:`Router.node`.)
        :type celery_task: A celery task decorator, in any form
        :param message_class: wrapper class for messages passed to nodes
        :type message_class: :py:class:`emit.message.Message` or subclass

        :exceptions: None
        :returns: None
        '''
        self.routes = initial_routes or {}
        self.fields = {}
        self.functions = {}
        self.celery_task = celery_task
        self.message_class = message_class or Message

        self.logger = logging.getLogger(__name__ + '.Router')
        self.logger.debug('Initialized Router')

    def __call__(self, **kwargs):
        '''\
        Route a message to all nodes marked as entry points.

        .. note::
           This function does not optionally accept a single argument
           (dictionary) as other points in this API do - it must be expanded to
           keyword arguments in this case.
        '''
        self.logger.info('Calling entry point with %r', kwargs)
        self.route('__entry_point', kwargs)

    def node(self, fields, subscribe_to=None, celery_task=None, entry_point=False):
        '''\
        Decorate a function to make it a node.

        .. note::
           decorating as a node changes the function signature. Nodes should
           accept a single argument, which will be a
           :py:class:`emit.message.Message`. Nodes can be called directly by
           providing a dictionary argument or a set of keyword arguments. Other
           uses will raise a ``TypeError``.

        :param fields: fields that this function returns
        :type fields: ordered iterable of :py:class:`str`
        :param subscribe_to: functions in the graph to subscribe to
        :type subscribe_to: :py:class:`str` or iterable of :py:class:`str`
        :param celery_task: celery task to apply to only this node. Use this to
                            add custom celery attributes (like rate limiting)
        :type celery_task: any celery task type
        :param entry_point: Set to ``True`` to mark this as an entry point -
                            that is, this function will be called when the
                            router is called directly.
        :type entry_point: :py:class:`bool`
        :returns: decorated and wrapped function, or decorator if called directly
        '''
        def outer(func):
            'outer level function'
            # create a wrapper function
            self.logger.debug('wrapping %s', func)
            @wraps(func)
            def inner(*args, **kwargs):
                'innermost function'
                message = self.get_message_from_call(*args, **kwargs)
                self.logger.info('calling "%s" with %r', name, message)
                result = func(message)

                # functions can return multiple values ("emit" multiple times)
                # by yielding instead of returning. Handle this case by making
                # a list of the results and processing them all after the
                # generator successfully exits. If we were to process them as
                # they came out of the generator, we might get a partially
                # processed input sent down the graph. This may be possible in
                # the future via a flag.
                if isinstance(result, GeneratorType):
                    results = [
                        self.wrap_result(name, item)
                        for item in result
                    ]
                    self.logger.debug(
                        '%s returned generator yielding %d items', func, len(results)
                    )

                    [self.route(name, item) for item in results]
                    return tuple(results)

                # the case of a direct return is simpler. wrap, route, and
                # return the value.
                else:
                    result = self.wrap_result(name, result)
                    self.logger.debug(
                        '%s returned single value %s', func, result
                    )
                    self.route(name, result)
                    return result

            # celery registers tasks by decorating them, and so do we, so the
            # user can pass a celery task and we'll wrap our code with theirs
            # in a nice package celery can execute.
            if celery_task or self.celery_task:
                if celery_task:
                    inner = celery_task(inner)
                else:
                    inner = self.celery_task(inner)

            # register the task in the graph
            name = self.get_name(inner)
            self.register(name, inner, fields, subscribe_to, entry_point)

            return inner

        return outer

    def get_message_from_call(self, *args, **kwargs):
        '''\
        Get message object from a call.

        :raises: :py:exc:`TypeError` (if the format is not what we expect)

        This is where arguments to nodes are turned into Messages. Arguments
        are parsed in the following order:

         - A single positional argument (a :py:class:`dict`)
         - No positional arguments and a number of keyword arguments
        '''
        if len(args) == 1 and isinstance(args[0], dict):
            # then it's a message
            self.logger.debug('called with arg dictionary')
            result = args[0]
        elif len(args) == 0 and kwargs != {}:
            # then it's a set of kwargs
            self.logger.debug('called with kwargs')
            result = kwargs
        else:
            # it's neither, and we don't handle that
            self.logger.error(
                'get_message_from_call could not handle "%r", "%r"',
                args, kwargs
            )
            raise TypeError('Pass either keyword arguments or a dictionary argument')

        return self.message_class(result)

    def register(self, name, func, fields, subscribe_to, entry_point):
        '''
        Register a named function in the graph

        :param name: name to register
        :type name: :py:class:`str`
        :param func: function to remember and call
        :type func: callable

        ``fields``, ``subscribe_to`` and ``entry_point`` are the same as in
        :py:meth:`Router.node`.
        '''

        self.fields[name] = fields
        self.functions[name] = func

        if subscribe_to:
            self.add_routes(subscribe_to, name)

        if entry_point:
            self.add_routes('__entry_point', name)

        self.logger.info('registered %s', name)

    def add_routes(self, origins, destination):
        '''
        Add routes to the routing dictionary

        :param origins: a number of origins to register
        :type origins: :py:class:`str` or iterable of :py:class:`str`
        :param destination: where the origins should point to
        :type destination: :py:class:`str`

        Routing dictionary takes the following form::

            {'node_a': set(['node_b', 'node_c']),
             'node_b': set(['node_d'])}

        '''
        if not isinstance(origins, list):
            origins = [origins]

        for origin in list(origins):
            self.routes.setdefault(origin, set())
            self.routes[origin].add(destination)
            self.logger.info('added route "%s" -> "%s"', origin, destination)

    def route(self, origin, message):
        '''\
        Using the routing dictionary, dispatch a message to all subscribers

        :param origin: name of the origin node
        :type origin: :py:class:`str`
        :param message: message to dispatch
        :type message: :py:class:`emit.message.Message` or subclass
        '''
        try:
            subs = self.routes[origin]
        except KeyError:
            # this is debug although it sounds dire. That's because every node,
            # no matter how inconsequential, tries to route. The log would be
            # very full if this was higher.
            self.logger.debug('no routes for "%s", exiting', origin)
            return

        for sub in subs:
            self.logger.debug('routing "%s" -> "%s"', origin, sub)
            self.dispatch(sub, message)

    def dispatch(self, subscriber, message):
        '''\
        dispatch a message to a named function

        :param subscriber: subscriber to dispatch to
        :type subscriber: :py:class:`str`
        :param message: message to dispatch
        :type message: :py:class:`emit.message.Message` or subclass

        Will delay the message (using celery) instead of calling it directly if
        possible.
        '''
        func = self.functions[subscriber]

        if hasattr(func, 'delay'):
            self.logger.debug('delaying %r', func)
            return func.delay(message)
        else:
            return func(message)

    def wrap_result(self, name, result):
        '''
        Wrap a result from a function with it's stated fields

        :param name: fields to look up
        :type name: :py:class:`str`
        :param result: return value from function. Will be converted to tuple.
        :type result: anything

        :returns: :py:class:`dict`
        '''
        if not isinstance(result, tuple):
            result = tuple([result])

        return dict(zip(self.fields[name], result))

    def get_name(self, func):
        '''
        Get the name to reference a function by

        :param func: function to get the name of
        :type func: callable

        Gets celery assigned name, if present (IE ``name`` instead of
        ``func_name``)
        '''
        if hasattr(func, 'name'):  # celery-decorated function
            return func.name

        return func.func_name
