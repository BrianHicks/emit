Logging
=======

Emit is set up to handle logging using Python's standard logger. It currently
uses the following levels:

 - ``DEBUG``: task registration and calls - very verbose
 - ``INFO``: route registration, receipts

So far there's been no need for anything above ``INFO``, but that may change in
the future.

Setting Up Logging
------------------

In some file (I recommend the file where the router is initialized, but your
project may vary) insert the following lines::

    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG) # or INFO etc.

Setting Up Logging in Django
----------------------------

In your logging config, add a logger for "emit". Like so::

    LOGGING = {
        # snip formatters, filters, handlers, etc
        'loggers': {
            # other loggers here
            'emit': {
                'handlers': ['console'],
                'level': 'INFO',
            }
        }
    }
