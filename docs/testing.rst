Testing
=======

.. module:: emit.router

Testing your functions is pretty easy. Just call
:py:class:`Router.disable_routing`. Something like this::

    from unittest import TestCase
    from yourapp.app import router
    from yourapp.tasks import do_task

    class DoTaskTests(TestCase):
        def setUp(self):
            router.disable_routing()

        def test_blah(self):
            assert True

To re-enable routing, you'd call :py:class:`Router.enable_routing`.
