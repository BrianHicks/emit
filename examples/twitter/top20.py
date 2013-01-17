from __future__ import print_function
from redis import Redis
redis = Redis()
print('there were %r tweets, here are the top 20 words:' % redis.get('tweet_count'))
print()
for i, (word, score) in enumerate(redis.zrevrange('tweet_word_counts', 0, 19, True)):
    print('%d:\t%s\t(%d words)' % (i + 1, word, score))
