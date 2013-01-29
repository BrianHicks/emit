Extending Router
================

To extend ``emit.Router`` (for example, to add a new dispatch backend) it's
most helpful to override the following methods:

``__init__(self, your_args, *args, **kwargs)``
    This is the ``__init__`` pattern used by the current dispatch backends.

``dispatch(origin, destination, message)``
    Do dispatching. Typically passes along ``origin`` (as
    ``_origin``) with the message.

``wrap_node(node, options)``
    Given a wrapped function (``node``), do additional processing on the
    function or node. Unhandled arguments to ``Router.node`` are passed as a
    dictionary as ``options``.

Example
-------

See the following example (the current ``RQRouter`` implementation):

.. literalinclude:: ../../emit/router.py
   :pyobject: RQRouter
