from __future__ import print_function
import random

from emit import Router
from emit.message import NoResult
from redis import Redis

redis = Redis()
router = Router()


@router.transaction('ensure_count')
@router.node(('n',))
def emit_n(msg):
    for n in range(msg.count):
        yield n


def rollback_incr(msgs):
    for msg in msgs:
        redis.decr(str(msg.n), 1)


@router.transaction('ensure_count', rollback_incr)
@router.node(('n', 'count'), 'graph.emit_n')
def incr(msg):
    redis.incr(str(msg.n), 1)


@router.transaction('ensure_count')
@router.node(tuple(), 'graph.emit_n')
def sometimes_fail(msg):
    if random.random() > 0.8:
        raise ValueError('random was greater than 0.8')

    return NoResult
