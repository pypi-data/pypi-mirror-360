import unittest
from orionis.test.output.dumper import TestDumper

class SyncTestCase(unittest.TestCase, TestDumper):
    """
    Base test case for sync unit tests.
    """

    def setUp(self):
        """
        Synchronous setup method called before each test.
        """
        super().setUp()
        self.onSetup()

    def tearDown(self):
        """
        Synchronous teardown method called after each test.
        """
        self.onTeardown()
        super().tearDown()

    def onSetup(self):
        """
        Hook for subclasses to add setup logic.
        """
        pass

    def onTeardown(self):
        """
        Hook for subclasses to add teardown logic.
        """
        pass