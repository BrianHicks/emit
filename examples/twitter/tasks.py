from redis import Redis
from app import router

redis = Redis()

@router.node(['tweet'])
def tweet_text(msg):
    'given a twitter API response, get the tweet content'
    if 'text' in msg.response:
        return msg.response['text']

@router.node(['word'], 'tasks.tweet_text')
def clean_words(msg):
    for word in msg.tweet.strip().split(' '):
        if not word.startswith('@') and not word.startswith('#'):
            yield word

@router.node(['word', 'count'], 'tasks.clean_words')
def tally_word(msg):
    return msg.word, redis.zincrby('tweet_word_counts', msg.word, 1)
