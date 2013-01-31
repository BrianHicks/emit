def skipIf(condition, message):
    try:
        from unittest import skipIf
        return skipIf(condition, message)
    except ImportError:  # skipIf/skip not implemented
        if condition:
            return lambda x: None
        else:
            return lambda x: x
