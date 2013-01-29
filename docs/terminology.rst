Terminology
-----------

Graph
    A directed graph. Not actually implemented as an object, but referenced
    throughout the project as the final construct of a router, nodes, and
    subscriptions. You can generate an image of the graph using the
    :doc:`emit-digraph <command-line-utilities>` utility.

Router
    An object (implemented in :py:class:`emit.router.Router` or subclasses)
    that keeps references to functions and their names and handles dispatch. It
    generally knows where everything is and where it's going.

Node
    A function or callable class that receives messages, processes them in its
    own way, and passes them on down the graph. In this sense, this output
    could be called a "stream".

Subscription/Route
    An edge in the graph. It is directed, and so only flows one way. Circular
    subscriptions can be created (by two nodes subscribing to each other's
    streams), but they have a high probability of creating
    an infinite loop and so should be used carefully. Subscriptions also can
    exist as a special case for an entry point to the graph.
