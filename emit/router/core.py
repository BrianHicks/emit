'router for emit'
from functools import wraps
import importlib
import logging
import re
from types import GeneratorType

from emit.messages import Message, NoResult


class Router(object):
    'A router object. Holds routes and references to functions for dispatch'
    def __init__(self, message_class=None, node_modules=None, node_package=None):
        '''\
        Create a new router object. All parameters are optional.

        :param message_class: wrapper class for messages passed to nodes
        :type message_class: :py:class:`emit.message.Message` or subclass
        :param node_modules: a list of modules that contain nodes
        :type node_modules: a list of :py:class:`str`, or ``None``.
        :param node_package: if any node_modules are relative, the path to base
                               off of.
        :type node_package: :py:class:`str`, or ``None``.

        :exceptions: None
        :returns: None
        '''
        self.routes = {}
        self.names = set()
        self.regexes = {}
        self.ignore_regexes = {}

        self.fields = {}
        self.functions = {}

        self.message_class = message_class or Message

        # manage imported packages, lazily importing before the first message
        # is routed.
        self.resolved_node_modules = []
        self.node_modules = node_modules or []
        self.node_package = node_package

        self.logger = logging.getLogger(__name__ + '.Router')
        self.logger.debug('Initialized Router')

        self.routing_enabled = True

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

    def wrap_as_node(self, func):
        'wrap a function as a node'
        name = self.get_name(func)

        @wraps(func)
        def wrapped(*args, **kwargs):
            'wrapped version of func'
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
                    if item is not NoResult
                ]
                self.logger.debug(
                    '%s returned generator yielding %d items', func, len(results)
                )

                [self.route(name, item) for item in results]
                return tuple(results)

            # the case of a direct return is simpler. wrap, route, and
            # return the value.
            else:
                if result is NoResult:
                    return result

                result = self.wrap_result(name, result)
                self.logger.debug(
                    '%s returned single value %s', func, result
                )
                self.route(name, result)
                return result

        return wrapped

    def node(self, fields, subscribe_to=None, entry_point=False, ignore=None,
             **wrapper_options):
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
        :param subscribe_to: functions in the graph to subscribe to. These
                             indicators can be regular expressions.
        :type subscribe_to: :py:class:`str` or iterable of :py:class:`str`
        :param ignore: functions in the graph to ignore (also uses regular
                       expressions.) Useful for ignoring specific functions in
                       a broad regex.
        :type ignore: :py:class:`str` or iterable of :py:class:`str`
        :param entry_point: Set to ``True`` to mark this as an entry point -
                            that is, this function will be called when the
                            router is called directly.
        :type entry_point: :py:class:`bool`

        In addition to all of the above, you can define a ``wrap_node``
        function on a subclass of Router, which will need to receive node and
        an options dictionary. Any extra options passed to node will be passed
        down to the options dictionary. See
        :py:class:`emit.router.CeleryRouter.wrap_node` as an example.

        :returns: decorated and wrapped function, or decorator if called directly
        '''
        def outer(func):
            'outer level function'
            # create a wrapper function
            self.logger.debug('wrapping %s', func)
            wrapped = self.wrap_as_node(func)

            if hasattr(self, 'wrap_node'):
                self.logger.debug('wrapping node "%s" in custom wrapper', wrapped)
                wrapped = self.wrap_node(wrapped, wrapper_options)

            # register the task in the graph
            name = self.get_name(func)
            self.register(
                name, wrapped, fields, subscribe_to, entry_point, ignore
            )

            return wrapped

        return outer

    def resolve_node_modules(self):
        'import the modules specified in init'
        if not self.resolved_node_modules:
            try:
                self.resolved_node_modules = [
                    importlib.import_module(mod, self.node_package)
                    for mod in self.node_modules
                ]
            except ImportError:
                self.resolved_node_modules = []
                raise

        return self.resolved_node_modules

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

    def register(self, name, func, fields, subscribe_to, entry_point, ignore):
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

        self.register_route(subscribe_to, name)

        if ignore:
            self.register_ignore(ignore, name)

        if entry_point:
            self.add_entry_point(name)

        self.logger.info('registered %s', name)

    def add_entry_point(self, destination):
        '''\
        Add an entry point

        :param destination: node to route to initially
        :type destination: str
        '''
        self.routes.setdefault('__entry_point', set()).add(destination)
        return self.routes['__entry_point']

    def register_route(self, origins, destination):
        '''
        Add routes to the routing dictionary

        :param origins: a number of origins to register
        :type origins: :py:class:`str` or iterable of :py:class:`str` or None
        :param destination: where the origins should point to
        :type destination: :py:class:`str`

        Routing dictionary takes the following form::

            {'node_a': set(['node_b', 'node_c']),
             'node_b': set(['node_d'])}

        '''
        self.names.add(destination)
        self.logger.debug('added "%s" to names', destination)

        origins = origins or []  # remove None
        if not isinstance(origins, list):
            origins = [origins]

        self.regexes.setdefault(destination, [re.compile(origin) for origin in origins])

        self.regenerate_routes()
        return self.regexes[destination]

    def register_ignore(self, origins, destination):
        '''
        Add routes to the ignore dictionary

        :param origins: a number of origins to register
        :type origins: :py:class:`str` or iterable of :py:class:`str`
        :param destination: where the origins should point to
        :type destination: :py:class:`str`

        Ignore dictionary takes the following form::

            {'node_a': set(['node_b', 'node_c']),
             'node_b': set(['node_d'])}

        '''
        if not isinstance(origins, list):
            origins = [origins]

        self.ignore_regexes.setdefault(destination, [re.compile(origin) for origin in origins])
        self.regenerate_routes()

        return self.ignore_regexes[destination]

    def regenerate_routes(self):
        'regenerate the routes after a new route is added'
        for destination, origins in self.regexes.items():
            # we want only the names that match the destination regexes.
            resolved = [
                name for name in self.names
                if name is not destination
                and any(origin.search(name) for origin in origins)
            ]

            ignores = self.ignore_regexes.get(destination, [])
            for origin in resolved:
                destinations = self.routes.setdefault(origin, set())

                if any(ignore.search(origin) for ignore in ignores):
                    self.logger.info('ignoring route "%s" -> "%s"', origin, destination)
                    try:
                        destinations.remove(destination)
                        self.logger.debug('removed "%s" -> "%s"', origin, destination)
                    except KeyError:
                        pass

                    continue

                if destination not in destinations:
                    self.logger.info('added route "%s" -> "%s"', origin, destination)

                destinations.add(destination)

    def disable_routing(self):
        'disable routing (usually for testing purposes)'
        self.routing_enabled = False

    def enable_routing(self):
        'enable routing (after calling ``disable_routing``)'
        self.routing_enabled = True

    def route(self, origin, message):
        '''\
        Using the routing dictionary, dispatch a message to all subscribers

        :param origin: name of the origin node
        :type origin: :py:class:`str`
        :param message: message to dispatch
        :type message: :py:class:`emit.message.Message` or subclass
        '''
        # side-effect: we have to know all the routes before we can route. But
        # we can't resolve them while the object is initializing, so we have to
        # do it just in time to route.
        self.resolve_node_modules()

        if not self.routing_enabled:
            return

        subs = self.routes.get(origin, set())

        for destination in subs:
            self.logger.debug('routing "%s" -> "%s"', origin, destination)
            self.dispatch(origin, destination, message)

    def dispatch(self, origin, destination, message):
        '''\
        dispatch a message to a named function

        :param destination: destination to dispatch to
        :type destination: :py:class:`str`
        :param message: message to dispatch
        :type message: :py:class:`emit.message.Message` or subclass
        '''
        func = self.functions[destination]
        self.logger.debug('calling %r directly', func)
        return func(_origin=origin, **message)

    def wrap_result(self, name, result):
        '''
        Wrap a result from a function with it's stated fields

        :param name: fields to look up
        :type name: :py:class:`str`
        :param result: return value from function. Will be converted to tuple.
        :type result: anything

        :raises: :py:exc:`ValueError` if name has no associated fields

        :returns: :py:class:`dict`
        '''
        if not isinstance(result, tuple):
            result = tuple([result])

        try:
            return dict(zip(self.fields[name], result))
        except KeyError:
            msg = '"%s" has no associated fields'
            self.logger.exception(msg, name)
            raise ValueError(msg % name)

    def get_name(self, func):
        '''
        Get the name to reference a function by

        :param func: function to get the name of
        :type func: callable
        '''
        if hasattr(func, 'name'):
            return func.name

        return '%s.%s' % (
            func.__module__,
            func.__name__
        )
