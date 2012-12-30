'router for emit'
from collections import namedtuple
from functools import wraps
from types import GeneratorType

class Router(object):
    def __init__(self, initial_routes=None):
        self.routes = initial_routes or {}
        self.fields = {}

    def node(self, fields, subscribes_to=None):
        'decorator for nodes connecting the emit graph'
        def outer(func):
            'outer level function'
            self.fields[func.func_name] = namedtuple(func.func_name + '_fields', fields)

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

                    #[self.route(item) for item in results]
                    return tuple(results)

                else:
                    result = self.wrap_result(func.func_name, result)
                    #self.route(item)
                    return result

            return inner

        return outer

    def add_routes(self, origins, destination):
        'add routes to the routing dictionary'
        for origin in list(origins):
            self.routes.setdefault(origin, set())
            self.routes[origin].add(destination)

    def wrap_result(self, name, result):
        'wrap a result in the namedtuple'
        if not isinstance(result, tuple):
            result = tuple([result])

        return self.fields[name](*result)

