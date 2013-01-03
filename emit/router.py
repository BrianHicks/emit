'router for emit'
from collections import namedtuple
from functools import wraps
from types import GeneratorType

class Router(object):
    def __init__(self, initial_routes=None, celery_task=None):
        self.routes = initial_routes or {}
        self.fields = {}
        self.functions = {}
        self.celery_task = celery_task

    def node(self, fields, subscribe_to=None, celery_task=None):
        'decorator for nodes connecting the emit graph'
        def outer(func):
            'outer level function'
            # create a wrapper function
            @wraps(func)
            def inner(*args, **kwargs):
                'innermost function'
                # TODO: handle the case of calling a function directly
                result = func(*args, **kwargs)

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

                    [self.route(name, item) for item in results]
                    return tuple(results)

                # the case of a direct return is simpler. wrap, route, and
                # return the value.
                else:
                    result = self.wrap_result(name, result)
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
            self.register(name, inner, fields, subscribe_to)

            return inner

        return outer

    def register(self, name, func, fields, subscribe_to):
        'register a name in the graph'
        self.fields[name] = namedtuple('message', fields)
        self.functions[name] = func

        if subscribe_to:
            self.add_routes(subscribe_to, name)

    def add_routes(self, origins, destination):
        'add routes to the routing dictionary'
        if not isinstance(origins, list):
            origins = [origins]

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
        if hasattr(func, 'name'):  # celery-decorated function
            return func.name

        return func.func_name
