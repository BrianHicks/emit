from redis import Redis
from app import app, router

@router.node(('word',), entry_point=True)
def emit_words(msg):
    for word in msg.document.strip().split(' '):
        yield word

@router.node(('word', 'count'), subscribe_to='tasks.emit_words', celery_task=app.task(rate_limit='5/s'))
def tally_word(msg):
    redis = Redis()
    return msg.word, redis.zincrby('celery_emit_example', msg.word, 1)
