# Emit

[![Build Status](https://travis-ci.org/BrianHicks/emit.png?branch=master)](https://travis-ci.org/BrianHicks/emit)

Emit gives you subscriptions to function results. Data pipelines and other fun
things abound. Observe:

```python
# router.py
from emit.router import Router

router = Router()

# tasks.py (or other like file)
from .router import router

@router.node(['n'])
def yield_n(n):
    for i in range(n):
        yield i

@router.node(['square'], ['yield_n'])
def square(msg):
    result = msg.n ** 2
    redis.sadd('squares', result)
    return result

# from the repl
>>> yield_n(5)
...
>>> redis.smembers('squares')
set([0, 1, 4, 9, 16])
```

## This is not really ready for production

It's all in one Python process right now. Next steps are adding support for
queue services like Celery and RQ. Watch this repo!
