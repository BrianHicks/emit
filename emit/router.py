'router for emit'
from functools import wraps

class Router(object):
    def __init__(self, initial_routes=None):
        self.routes = initial_routes or {}

    def node(self, field_names, subscribes_to=None):
        'decorator for nodes connecting the emit graph'
        def outer(func):
            'outer level function'

            if subscribes_to:
                self.add_routes(subscribes_to, func.func_name)

            @wraps(func)
            def inner(*args, **kwargs):
                'innermost function'
                return func(*args, **kwargs)

            return inner

        return outer

    def add_routes(self, origins, destination):
        'add routes to the routing dictionary'
        for origin in list(origins):
            self.routes.setdefault(origin, set())
            self.routes[origin].add(destination)
