Changelog
=========

0.5.0
-----

 - Nodes which return single values will now be wrapped in a tuple, for
   consistency with generator nodes. Routing will proceed as before.

0.4.0
-----

 - Optional install bundles for installing with RQ or Celery
 - Move modules around to make API more consistent. Notably,
   ``emit.router.Router`` is now in ``emit.router.core`` with RQ and Celery
   backends in ``emit.router.rq`` and ``emit.router.celery``, respectively.
 - Huge cleanup of codebase in general, especially test suite and ``setup.py``.

0.3.0
-----

 - Better documentation
 - :doc:`RQ support <distributing-work/rq>`

0.2.0
-----

 - New argument for ``node``: ``ignores``. Pass it some regex to ignore items
   in otherwise broad subscriptions.
 - Add support for Python 2.6

0.1.0
-----

 - Initial Release to PyPI
