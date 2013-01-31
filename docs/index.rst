Welcome to Emit's documentation!
================================

Emit is a library that hooks into distributed systems like Celery or RQ (or
just local memory) to provide subscriptions and notifications for your
functions. It is designed to make processing streams of information a whole lot
easier.

You may want to start at :doc:`getting-started`. Other highlights include
integration with :doc:`Celery <distributing-work/celery>` and :doc:`RQ
<distributing-work/rq>` and Emit's :doc:`multi-language <multilang>`
capabilities.

Contents:

.. toctree::
   :maxdepth: 1

   getting-started
   distributing-work/index
   multilang
   terminology
   regex-routing
   command-line-utilities
   logging
   testing
   api-documentation
   changelog

Supported Pythons:

* `CPython 2.6`_
* `CPython 2.7`_
* `CPython 3.2`_
* `CPython 3.3`_
* `PyPy 1.9`_

.. _CPython 2.6: http://docs.python.org/2.6/
.. _CPython 2.7: http://docs.python.org/2.7/
.. _Cpython 3.2: http://docs.python.org/3.2/
.. _Cpython 3.3: http://docs.python.org/3.3/
.. _PyPy 1.9: http://pypy.org/index.html

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


License
=======

.. literalinclude:: ../LICENSE.md
