from emit import Router
from emit.message import NoResult
from redis import Redis

router = Router()
redis = Redis()

def prefix(name):
    return '%s.%s' % (__name__, name)

@router.node(('key', 'value'), entry_point=True)
def parse_querystring(msg):
    'parse a querystring into keys and values'
    for part in msg.querystring.strip().lstrip('?').split('&'):
        key, value = part.split('=')
        yield key, value

@router.node(('key', 'value', 'count'), prefix('parse_querystring'))
def count_keyval(msg):
    count = redis.zincrby('querystring_count.%s' % msg.key, msg.value, 1)
    return msg.key, msg.value, count

@router.node(tuple(), '.+')
def notify_on_emit(msg):
    redis.publish('notify_on_emit.%s' % msg._origin, msg.as_json())
    return NoResult
