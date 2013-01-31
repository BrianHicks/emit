API Documentation
=================

Router
------

.. module:: emit.router.core

.. autoclass:: Router

   .. automethod:: Router.__init__

   .. automethod:: Router.__call__

   .. automethod:: Router.node

      **Examples**

      *Multiple fields*::

          @router.node(['quotient', 'remainder'])
          def division_with_remainder(msg):
              return msg.numer / msg.denom, msg.numer % msg.denom

      This function would end up returing a dictionary that looked something like::

          {'quotient': 2, 'remainder': 1}

      The next node in the graph would recieve a
      :py:class:`emit.message.Message` with "quotient" and "remainder"
      fields.

      *Emitting multiple values*::

          @router.node(['word'])
          def parse_document(msg):
              for word in msg.document.clean().split(' '):
                  yield word

      If the function returns a generator, Emit will gather the values together
      and make sure the generator exits cleanly before returning (but this may
      change in the future via a flag.) Therefore, the return value will look
      like this::

          ({'word': "I've"},
           {'word': 'got'},
           {'word': 'a'},
           {'word': 'lovely'},
           {'word': 'bunch'},
           {'word': 'of'},
           {'word': 'coconuts'})

      Each message in the tuple will be passed on individually in the graph.

   .. automethod:: Router.add_entry_point
   .. automethod:: Router.disable_routing
   .. automethod:: Router.dispatch
   .. automethod:: Router.enable_routing
   .. automethod:: Router.get_message_from_call
   .. automethod:: Router.get_name
   .. automethod:: Router.regenerate_routes
   .. automethod:: Router.register
   .. automethod:: Router.register_ignore
   .. automethod:: Router.register_route
   .. automethod:: Router.resolve_node_modules
   .. automethod:: Router.route
   .. automethod:: Router.wrap_as_node
   .. automethod:: Router.wrap_result

.. autoclass:: CeleryRouter
   :members:
   :special-members:

.. autoclass:: RQRouter
   :members:
   :special-members:

Message
-------

.. module:: emit.message

.. autoclass:: Message
   :members:

.. autoclass:: NoResult
   :members:

Multilang
---------

.. module:: emit.multilang

.. autoclass:: ShellNode
   :members:

   .. automethod:: ShellNode.__call__
