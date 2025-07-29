
from orionis.services.asynchrony.coroutines import Coroutine
from orionis.services.asynchrony.exceptions.coroutine_exception import OrionisCoroutineException
from orionis.unittesting import TestCase

class TestServicesAsynchronyCoroutine(TestCase):

    async def testExecuteWithActiveEventLoop(self):
        """
        Test the execution of a coroutine within an active event loop.
        This test simulates a scenario where the coroutine is executed in an environment with an active event loop,
        such as a Jupyter notebook or a Starlette application.
        """
        async def sample_coroutine():
            return "Hello, World!"

        result = await Coroutine(sample_coroutine()).run()
        self.assertEqual(result, "Hello, World!")

    def testExecuteWithoutActiveEventLoop(self):
        """
        Test the execution of a coroutine without an active event loop.
        This test simulates a scenario where the coroutine is executed in a synchronous context without an active event loop.
        """
        async def sample_coroutine():
            return "Hello, World!"

        result = Coroutine(sample_coroutine()).run()
        self.assertEqual(result, "Hello, World!")

    def testExecuteWithNonCoroutine(self):
        """
        Test the execution of a non-coroutine object.
        This test checks that a TypeError is raised when a non-coroutine object is passed to the execute method.
        """
        def sample_no_coroutine():
            return "Hello, World!"

        with self.assertRaises(OrionisCoroutineException):
            Coroutine(sample_no_coroutine())