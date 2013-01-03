'router for emit'
from collections import namedtuple
from functools import wraps
from types import GeneratorType

class Router(object):
    def __init__(self, initial_routes=None):
        self.routes = initial_routes or {}
        self.fields = {}
        self.functions = {}

    def node(self, fields, subscribes_to=None):
        'decorator for nodes connecting the emit graph'
        def outer(func):
            'outer level function'
            name = self.get_name(func)
            self.fields[name] = namedtuple(name + '_fields', fields)
            self.functions[name] = func

            if subscribes_to:
                self.add_routes(subscribes_to, name)

            @wraps(func)
            def inner(*args, **kwargs):
                'innermost function'
                result = func(*args, **kwargs)

                if isinstance(result, GeneratorType):
                    results = []
                    for item in result:
                        results.append(self.wrap_result(name, item))

                    [self.route(name, item) for item in results]
                    return tuple(results)

                else:
                    result = self.wrap_result(name, result)
                    self.route(name, result)
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

    def get_name(self, func):
        'get the name of a function'
        return func.func_name
