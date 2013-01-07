# Emit

Emit is a Python library for realtime data processing. It can [distribute work
with Celery][celery-docs], [coordinate execution in other
languages][multilang-docs], and let you swing from the trees of your graph with
Tarzan-like precision.

A taste:

```python
from emit import router

router = Router()

@router.task(['word'], entry_point=True)
def parse_document(msg):
    for word in msg.document.strip().split(' '):
        yield word

@router.task(['word', 'count'], 'parse_document')
def count_word(msg):
    return msg.word, redis.zincrby('word_counts', msg.word, 1)

import random
document = 'the words in this document will be counted and emitted by count_words'.split(' ')
router(document=' '.join(random.choice(document) for i in range(20)))
```

Some Links:

 - [Project Documentation][docs]
 - [Travis][travis] ([![Build Status](https://travis-ci.org/BrianHicks/emit.png?branch=master)][travis])
 - [Github][github]
 - [Apache License][license]

[celery-docs]: https://emit.readthedocs.org/en/latest/celery.html "Celery Documentation"
[multilang-docs]: https://emit.readthedocs.org/en/latest/multilang.html "Multilang Documentation"
[docs]: http://emit.readthedocs.org/en/latest/ "Emit Documentation"
[travis]: https://travis-ci.org/BrianHicks/emit "Emit on Travis CI"
[github]: https://github.com/BrianHicks/emit "Emit on Github"
[license]: https://github.com/BrianHicks/emit/blob/master/LICENSE.md "Apache License"
