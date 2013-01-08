from collections import Counter
from emit import Router
import sys

router = Router()

def prefix(name):
    return '%s.%s' % (__name__, name)

@router.node(['word'], entry_point=True)
def words(msg):
    print 'got document'
    for word in msg.document.strip().split(' '):
        yield word

WORDS = Counter()
@router.node(['word', 'count'], prefix('words'))
def count_word(msg):
    print 'got word (%s)' % msg.word

    global WORDS
    WORDS.update([msg.word])

    return msg.word, WORDS[msg.word]

if __name__ == '__main__':
    router(document=sys.stdin.read())

    print
    print 'Top 5 words:'
    for word, count in WORDS.most_common(5):
        print '    %s: %s' % (word, count)
