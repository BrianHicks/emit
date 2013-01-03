from redis import Redis
from app import router

redis = Redis()

@router.node(['word'])
def emit_words(instring):
    for word in instring.split(' '):
        yield word

@router.node(['count'], subscribe_to='tasks.emit_words')
def tally_word(msg):
    return redis.zincrby('celery_emit_example', msg.word, 1)
