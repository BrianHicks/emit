Using RQ to Distribute Processing
=================================

.. note::
   RQ does not currently work on Python 3. Emit should work with it (as it
   works with Python 2) when Python 3 support is ready.

RQ is a module that makes distributed processing easy. It's similar to Celery,
but simpler and only for Python and Redis. We'll be using the same example as
we did in the Celery example.

.. image:: ../../examples/celery/graph.png

Installing
----------

If you have a very recent version of pip, Emit can be installed pre-bundled
with RQ by installing with the following extra::

    pip install emit[rq-routing]

Otherwise, you'll need to install these dependencies::

    rq>=0.3.4
    redis>=2.7.2

Setting up RQ
-------------

Create an ``app.py`` file for your RQ Router initializaition code to live in:

.. literalinclude:: ../../examples/rq/app.py
   :language: python
   :linenos:

The ``RQRouter`` class only needs to know what Redis connection you want to
use. The rest of the options are specified at the node level.

Next we'll define (in ``tasks.py``) a function to take a document and emit each
word:

.. literalinclude:: ../../examples/rq/tasks.py
   :language: python
   :lines: 5-8

Without any arguments, RQ tasks will go to the 'default' queue. If you don't
want to mess with queues, this will *just work*.

If you want to set some attributes, however, you can:

.. literalinclude:: ../../examples/rq/tasks.py
   :language: python
   :lines: 11-14

Enqueued functions for this node will be put on the "words" node. You'll need
to specify which nodes to listen to when running ``rqworker``.

The available parameters:

+----------------+---------------------+------------------------------------------+
| parameter      | default             | effect                                   |
+================+=====================+==========================================+
| ``queue``      | ``'default'``       | specify a queue to route to.             |
+----------------+---------------------+------------------------------------------+
| ``connection`` | supplied connection | a different connection - be careful with |
|                |                     | this, as you'll need to specify the      |
|                |                     | connection string on the worker          |
+----------------+---------------------+------------------------------------------+
| ``timeout``    | ``None``            | timeout (in seconds) of a task           |
+----------------+---------------------+------------------------------------------+
| ``result_ttl`` | ``500``             | TTL (in seconds) of results              |
+----------------+---------------------+------------------------------------------+

Running the Graph
-----------------

We just need to start the RQ worker:

.. literalinclude:: ../../examples/rq/run.sh
   :language: sh

And enter the following on the command line to start something fun processing
(if you'd like, the relevant code is in ``examples/rq/kickoff.py`` in the
project directory, start it and get a prompt with ``ipython -i kickoff.py``):

.. literalinclude:: ../../examples/rq/kickoff.py
   :language: python

And you should see the rqworker window quickly scrolling by with updated
totals.  Run the command a couple more times, if you like, and you'll see the
totals keep going up.

Performance
-----------

Because of the way RQ forks tasks, the graph is rebuilt for every task. To
speed up this process, do it once on worker initialization. You can use this
snippet (adapted from the `RQ worker documentation`_)

.. _`RQ worker documentation`: http://python-rq.org/docs/workers/

.. literalinclude:: ../../examples/rq/worker.py
   :language: python
