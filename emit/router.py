'router for emit'
from collections import namedtuple
from functools import wraps
from types import GeneratorType

from .errors import RegistrationError

class Router(object):
    def __init__(self, initial_routes=None):
        self.routes = initial_routes or {}
        self.fields = {}
        self.functions = {}

    def node(self, fields, subscribes_to=None):
        'decorator for nodes connecting the emit graph'
        def outer(func):
            'outer level function'
            self.fields[func.func_name] = namedtuple(func.func_name + '_fields', fields)
            self.functions[func.func_name] = func

            if subscribes_to:
                self.add_routes(subscribes_to, func.func_name)

            @wraps(func)
            def inner(*args, **kwargs):
                'innermost function'
                result = func(*args, **kwargs)

                if isinstance(result, GeneratorType):
                    results = []
                    for item in result:
                        results.append(self.wrap_result(func.func_name, item))

                    [self.route(func.func_name, item) for item in results]
                    return tuple(results)

                else:
                    result = self.wrap_result(func.func_name, result)
                    self.route(func.func_name, result)
                    return result

            return inner

        return outer

    def add_routes(self, origins, destination):
        'add routes to the routing dictionary'
        for origin in list(origins):
            self.routes.setdefault(origin, set())
            self.routes[origin].add(destination)

    def route(self, origin, message):
        'route messages to multiple subscribers'
        try:
            subs = self.routes[origin]
        except KeyError:
            return

        for sub in subs:
            self.functions[sub](message)

    def wrap_result(self, name, result):
        'wrap a result in the namedtuple'
        if not isinstance(result, tuple):
            result = tuple([result])

        return self.fields[name](*result)
