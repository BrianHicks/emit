def passthru(condition, message):
    def outer(func):
        if condition:
            return func

    return outer


def _skipIf(condition, message):
    def outer(func):
        if condition:
            return skip(message)(func)
        else:
            return func

    return outer

try:
    from unittest import skipIf
except ImportError:
    try:
        from unittest import skip
        skipIf = _skipIf
    except ImportError:
        skipIf = passthru
