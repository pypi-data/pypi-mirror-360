import unittest
from orionis.test.output.dumper import TestDumper

class AsyncTestCase(unittest.IsolatedAsyncioTestCase, TestDumper):
    """
    Base test case for async unit tests.
    """

    async def asyncSetUp(self):
        """
        Asynchronous setup method for test cases.

        This method is called before each test coroutine is run. It first calls the parent
        class's asyncSetUp method to perform any necessary setup defined in the superclass,
        then calls the onAsyncSetup coroutine for additional setup specific to this test case.

        Override onAsyncSetup to implement custom asynchronous setup logic.

        Returns:
            Awaitable: Completes when setup is finished.
        """
        await super().asyncSetUp()
        await self.onAsyncSetup()

    async def asyncTearDown(self):
        """
        Asynchronous teardown method called after each test.

        This method performs any necessary asynchronous cleanup by first calling
        `onAsyncTeardown()` for custom teardown logic, then invoking the superclass's
        `asyncTearDown()` to ensure proper teardown in the class hierarchy.
        """
        await self.onAsyncTeardown()
        await super().asyncTearDown()

    async def onAsyncSetup(self):
        """
        Asynchronous setup method to be executed before running tests.

        This method can be overridden to perform any asynchronous initialization
        required for the test case. By default, it does nothing.

        Returns:
            None
        """
        pass

    async def onAsyncTeardown(self):
        """
        Asynchronous teardown method to be executed after each test case.

        This method can be overridden to perform any necessary cleanup operations
        that need to run asynchronously after the completion of a test case.
        """
        pass
