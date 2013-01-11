from redis import Redis
from app import router
from emit.message import NoResult

redis = Redis()

@router.node(('tweet',), entry_point=True)
def tweet_text(msg):
    'given a twitter API response, get the tweet content'
    return msg.response.get('text', NoResult)

@router.node(('word',), 'tasks.tweet_text')
def clean_words(msg):
    for word in msg.tweet.strip().split(' '):
        if word and not word.startswith('@') and not word.startswith('#'):
            yield word

@router.node(('word', 'count'), 'tasks.clean_words')
def tally_word(msg):
    return msg.word, redis.zincrby('tweet_word_counts', msg.word, 1)

@router.node(('message_count',), 'tasks.tweet_text')
def count_messages(msg):
    return redis.incr('tweet_count', 1)

@router.node(('call_count',), '.+')
def count_calls(msg):
    return redis.zincrby('tweet_call_counts', msg._origin, 1)
