from unittest import TestLoader
from unittest.mock import MagicMock, patch
from orionis.test.cases.asynchronous import AsyncTestCase
from orionis.test.core.unit_test import UnitTest
from orionis.test.enums import ExecutionMode
from unittest import (
    TestSuite as StandardTestSuite,
    TestResult as StandardTestResult
)

class TestTestingUnit(AsyncTestCase):

    async def testDefaultConfiguration(self) -> None:
        """
        Test that UnitTest initializes with correct default configuration values.

        Notes
        -----
        Verifies that all default attributes are set as expected upon initialization.
        """
        unit_test = UnitTest()
        self.assertIsInstance(unit_test.loader, TestLoader)
        self.assertIsInstance(unit_test.suite, StandardTestSuite)

    async def testConfigureMethod(self) -> None:
        """
        Test the `configure` method for correct configuration updates.
        This test verifies that all configuration parameters of the `UnitTest` class
        can be updated through the `configure` method and that the changes are
        reflected in the instance attributes.

        Parameters
        ----------
        self : TestCase
            The test case instance.

        Notes
        -----
        The test checks the following configuration parameters:
        - verbosity
        - execution_mode
        - max_workers
        - fail_fast
        - print_result
        - throw_exception
        It also asserts that the `configure` method returns the instance itself.
        """
        unit_test = UnitTest()
        configured = unit_test.configure(
            verbosity=1,
            execution_mode=ExecutionMode.PARALLEL,
            max_workers=8,
            fail_fast=True,
            print_result=False,
            throw_exception=True
        )

        self.assertEqual(unit_test.verbosity, 1)
        self.assertEqual(unit_test.execution_mode, ExecutionMode.PARALLEL.value)
        self.assertEqual(unit_test.max_workers, 8)
        self.assertTrue(unit_test.fail_fast)
        self.assertFalse(unit_test.print_result)
        self.assertTrue(unit_test.throw_exception)
        self.assertEqual(configured, unit_test)

    async def testDiscoverTestsInModule(self) -> None:
        """
        Test that `discoverTestsInModule` correctly loads tests from a module.

        Verifies that tests can be discovered from a module and added to the test suite.

        Notes
        -----
        This test mocks the loader's `loadTestsFromName` method to ensure that
        `discoverTestsInModule` calls it with the correct arguments and that the
        returned suite is handled as expected.
        """
        unit_test = UnitTest()
        with patch.object(unit_test.loader, 'loadTestsFromName') as mock_load:
            mock_load.return_value = StandardTestSuite()
            result = unit_test.discoverTestsInModule(module_name='test_module')

            mock_load.assert_called_once_with(name='test_module')
            self.assertEqual(result, unit_test)
            self.assertEqual(len(unit_test.suite._tests), 0)

    async def testFlattenTestSuite(self) -> None:
        """
        Test the _flattenTestSuite method for correct flattening of nested test suites.
        This test verifies that the _flattenTestSuite method of the UnitTest class
        correctly flattens both simple and nested unittest suites into a single list
        of test cases.

        Parameters
        ----------
        self : TestCase
            The test case instance.

        Notes
        -----
        - Ensures that nested suites are recursively flattened.
        - Asserts that all test cases from nested suites are present in the flattened result.
        """
        unit_test = UnitTest()
        test_case1 = MagicMock()
        test_case2 = MagicMock()

        nested_suite = StandardTestSuite()
        nested_suite.addTest(test_case1)
        nested_suite.addTest(test_case2)

        main_suite = StandardTestSuite()
        main_suite.addTest(nested_suite)

        flattened = unit_test._UnitTest__flattenTestSuite(main_suite)
        self.assertEqual(len(flattened), 2)
        self.assertIn(test_case1, flattened)
        self.assertIn(test_case2, flattened)

    async def testMergeTestResults(self) -> None:
        """
        Test the _mergeTestResults method for correct merging of test results.
        Ensures that the method accurately combines the number of tests run,
        as well as the lists of failures and errors from individual test results.

        Notes
        -----
        - Verifies that the total number of tests run is updated correctly.
        - Checks that failures and errors are merged without loss of information.
        """
        unit_test = UnitTest()
        combined = StandardTestResult()
        individual = StandardTestResult()

        individual.testsRun = 2
        individual.failures = [('test1', 'failure')]
        individual.errors = [('test2', 'error')]

        unit_test._UnitTest__mergeTestResults(combined, individual)
        self.assertEqual(combined.testsRun, 2)
        self.assertEqual(len(combined.failures), 1)
        self.assertEqual(len(combined.errors), 1)

    async def testClearTests(self) -> None:
        """
        Test the clearTests method to ensure it resets the test suite.
        This test verifies that after adding a mock test to the suite and calling
        the clearTests method, the suite is emptied as expected.

        Steps
        -----
        1. Create an instance of UnitTest.
        2. Add a mock test to the test suite.
        3. Call the clearTests method.
        4. Assert that the test suite is empty.

        Assertions
        ----------
        - The length of the test suite should be zero after calling clearTests.
        """
        unit_test = UnitTest()
        mock_test = MagicMock()
        unit_test.suite.addTest(mock_test)

        unit_test.clearTests()
        self.assertEqual(len(unit_test.suite._tests), 0)

    async def testGetTestNames(self) -> None:
        """
        This test verifies that the `getTestNames` method of the `UnitTest` class
        correctly extracts and returns the identifiers of tests present in the test suite.

        Notes
        -----
        - Mocks a test case with a predefined identifier.
        - Adds the mock test to the test suite.
        - Asserts that the returned list of test names matches the expected value.
        """
        unit_test = UnitTest()
        mock_test = MagicMock()
        mock_test.id.return_value = 'test_id'
        unit_test.suite.addTest(mock_test)

        names = unit_test.getTestNames()
        self.assertEqual(names, ['test_id'])

    async def testGetTestCount(self) -> None:
        """
        Test that `getTestCount` returns the correct number of tests.

        Verifies that the count matches the number of tests in the suite.

        Notes
        -----
        - Adds two mock tests to the suite.
        - Asserts that `getTestCount` returns 2.

        Returns
        -------
        None
        """
        unit_test = UnitTest()
        mock_test1 = MagicMock()
        mock_test2 = MagicMock()
        unit_test.suite.addTest(mock_test1)
        unit_test.suite.addTest(mock_test2)

        count = unit_test.getTestCount()
        self.assertEqual(count, 2)