Welcome to Emit's documentation!
================================

Emit is a library that hooks into distributed systems like Celery or RQ (or
just local memory) to provide subscriptions and notifications for your
functions. It is designed to make processing streams of information a whole lot
easier.

You may want to start at :doc:`getting-started`. Other highlights include
integration with :doc:`Celery <celery>` and :doc:`RQ <rq>` and Emit's
:doc:`multi-language <multilang>` capabilities.

Supported Pythons:

* CPython 2.6
* CPython 2.7
* CPython 3.2
* PyPy 1.9

Contents:

.. toctree::
   :maxdepth: 1

   getting-started
   celery
   rq
   multilang
   regex-routing
   command-line-utilities
   logging
   testing
   api-documentation
   glossary
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


License
=======

.. literalinclude:: ../LICENSE.md
