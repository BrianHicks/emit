Using Emit in Other Languages
=============================

You can use Emit in other languages through the multilang API.

Defining Tasks
--------------

We're going to define a node that takes a number and emits each integer in that
range. Let's do it with Ruby! (why not?)

.. literalinclude:: ../examples/multilang/test.rb
   :language: ruby

(the equivalent in Python is in ``examples/multilang/test.py``)

The messages passed in and out are expected to be in JSON format. Output from
the functions should be json strings separated by newlines.

Creating a Node
---------------

We'll be subclassing :py:class:`emit.multilang.ShellNode` to tell emit how
to execute our task:

.. literalinclude:: ../examples/multilang/graph.py
   :language: python
   :lines: 12-14

After that, you can call your node and subscribe as normal.
