Distributing Work
=================

Emit follows the philosophy that routing execution of tasks over the network is
best handled by an external library. Currently, there are two integrations:
:doc:`RQ <rq>` and :doc:`Celery <celery>`.

In addition, you may want to :doc:`write your own <extending-router>` for an
as-of-yet unknown backend.

Contents
--------

.. toctree::
   :maxdepth: 1

   rq
   celery
   extending-router
