from orionis.test.cases.test_case import TestCase

class TestExample(TestCase):
    """
    Unit tests for basic example functionality.
    """

    def testUnitExample(self):
        """
        Test that basic equality assertions work as expected.

        Asserts
        -------
        1 == 1 : bool
            Ensures that the integer 1 is equal to itself.
        2 == 2 : bool
            Ensures that the integer 2 is equal to itself.
        """
        # Check if 1 equals 1
        self.assertEqual(2, 2)

        # Check if 2 equals 2
        self.assertEqual(3, 3)