Emit
====

Emit is a Python library for realtime data processing. It can distribute work
with `Celery
<https://emit.readthedocs.org/en/latest/distributing-work/celery.html>`_ or `RQ
<https://emit.readthedocs.org/en/latest/distributing-work/rq.html>`_,
`coordinate execution in other languages
<https://emit.readthedocs.org/en/latest/multilang.html>`_, and let you swing
from the trees of your graph with Tarzan-like precision.

A taste:

.. code:: python

    from emit import router

    router = Router()

    @router.node(['word'], entry_point=True)
    def parse_document(msg):
        for word in msg.document.strip().split(' '):
            yield word

    @router.node(['word', 'count'], 'parse_document')
    def count_word(msg):
        return msg.word, redis.zincrby('word_counts', msg.word, 1)

    import random
    document = 'the words in this document will be counted and emitted by count_word'.split(' ')
    router(document=' '.join(random.choice(document) for i in range(20)))

So how do you get it? On PyPI!

::

    pip install emit

Some Links:

-  `Project Documentation <http://emit.readthedocs.org/en/latest/>`__
-  `Travis <https://travis-ci.org/BrianHicks/emit>`__ (|Build Status|)
-  `Github <https://github.com/BrianHicks/emit>`__
-  `Apache
   License <https://github.com/BrianHicks/emit/blob/master/LICENSE.md>`__

Supported Pythons:

-  CPython 2.6
-  CPython 2.7
-  CPython 3.2
-  PyPy 1.9

.. |Build Status| image:: https://travis-ci.org/BrianHicks/emit.png?branch=master
   :target: https://travis-ci.org/BrianHicks/emit

Installing from source/development branch:

Emit's releases are fairly frequent, so you should be good to use a released
version. However, if you need something currently not in a version, try the
``develop`` branch::

    pip install git+git://github.com/BrianHicks/emit.git@develop

Just do be warned that things will break. And be sure to check `Travis
<https://travis-ci.org/BrianHicks/emit>`__ to see if the platform you want is
currently passing. It should be, but maybe not.
