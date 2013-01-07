Glossary
--------

Some of the terms in this project may be a little rough. I'm still considering
what things should really be called here, but here's a primer:

 - *Router*: an object (implemented in :py:class:`emit.router.Router`) that
   keeps references to functions and their names and handles dispatch. It knows
   where everything is.

 - *Node*: a function or callable class that receives messages, processes them
   in it's own way, and passes them on down the graph.

 - *Subscription*: an edge in the graph - only flows one way.

 - *Graph*: a directed graph, like graph theory. A collection of nodes
   connected by subscriptions.
