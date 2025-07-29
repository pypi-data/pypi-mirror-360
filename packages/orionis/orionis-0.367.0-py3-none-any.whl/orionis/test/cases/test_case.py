import unittest
from orionis.test.output.dumper import TestDumper

class TestCase(unittest.IsolatedAsyncioTestCase, TestDumper):
    """
    Base test case for async unit tests.
    """

    async def asyncSetUp(self):
        """
        Asynchronous setup method called before each test.

        This method first calls the parent class's asyncSetUp method to ensure any inherited setup logic is executed.
        Then, it calls the onAsyncSetup method, which can be used to perform additional asynchronous setup specific to this test case.

        Override this method to customize asynchronous setup behavior for your tests.
        """
        await super().asyncSetUp()
        await self.onAsyncSetup()

    async def asyncTearDown(self):
        """
        Asynchronous teardown method called after each test.

        This method performs any necessary asynchronous cleanup by first invoking
        the custom `onAsyncTeardown` coroutine, followed by the superclass's
        `asyncTearDown` method to ensure proper teardown in the test lifecycle.
        """
        await self.onAsyncTeardown()
        await super().asyncTearDown()

    async def onAsyncSetup(self):
        """
        Hook for subclasses to add async setup logic.
        """
        pass

    async def onAsyncTeardown(self):
        """
        Hook for subclasses to add async teardown logic.
        """
        pass