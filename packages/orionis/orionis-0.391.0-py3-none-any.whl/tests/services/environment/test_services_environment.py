from orionis.services.environment.env import Env
from orionis.test.cases.asynchronous import AsyncTestCase

class TestServicesEnvironment(AsyncTestCase):

    async def testSetAndGetConstants(self):
        """
        Test storing and retrieving framework metadata constants using Env.set and Env.get.

        Imports several metadata constants from the `orionis.metadata.framework` module, sets each constant
        in the Env storage using `Env.set`, and verifies that the operation succeeds. Then retrieves each
        constant using `Env.get` and asserts that the retrieved value matches the original constant.

        Ensures
        -------
        - `Env.set` returns True for each constant.
        - `Env.get` returns the correct value for each constant.
        """
        from orionis.metadata.framework import (
            NAME, VERSION, AUTHOR, AUTHOR_EMAIL, DESCRIPTION,
            SKELETON, FRAMEWORK, DOCS, API, PYTHON_REQUIRES
        )
        constants = {
            "NAME": NAME,
            "VERSION": VERSION,
            "AUTHOR": AUTHOR,
            "AUTHOR_EMAIL": AUTHOR_EMAIL,
            "DESCRIPTION": DESCRIPTION,
            "SKELETON": SKELETON,
            "FRAMEWORK": FRAMEWORK,
            "DOCS": DOCS,
            "API": API,
            "PYTHON_REQUIRES": PYTHON_REQUIRES
        }
        for key, value in constants.items():
            result = Env.set(key, value)
            self.assertTrue(result)
        for key, value in constants.items():
            retrieved = Env.get(key)
            self.assertEqual(retrieved, value)

    async def testGetNonExistentKey(self):
        """
        Test that Env.get returns None for a non-existent environment key.

        Ensures
        -------
        - `Env.get` returns None when the key does not exist.
        """
        self.assertIsNone(Env.get("NON_EXISTENT_KEY"))

    async def testTypeHints(self):
        """
        Test that Env.set and Env.get correctly handle and preserve Python type hints.

        Sets environment variables with various data types (int, float, bool, str, list, dict, tuple, set)
        using the `Env.set` method, specifying the type as a string. Then retrieves each variable using
        `Env.get` and asserts that the returned value is of the expected Python type.

        Ensures
        -------
        - The returned value from `Env.get` matches the expected Python type for each variable.
        """

        # Set environment variables with type hints
        Env.set("TEST_INT", 42, 'int')
        Env.set("TEST_FLOAT", 3.14, 'float')
        Env.set("TEST_BOOL", True, 'bool')
        Env.set("TEST_STR", "Hello, World!", 'str')
        Env.set("TEST_LIST", [1, 2, 3], 'list')
        Env.set("TEST_DICT", {"key": "value"}, 'dict')
        Env.set("TEST_TUPLE", (1,2,3), 'tuple')
        Env.set("TEST_SET", {1, 2, 3}, 'set')

        # Retrieve and check types
        self.assertIsInstance(Env.get("TEST_INT"), int)
        self.assertIsInstance(Env.get("TEST_FLOAT"), float)
        self.assertIsInstance(Env.get("TEST_BOOL"), bool)
        self.assertIsInstance(Env.get("TEST_STR"), str)
        self.assertIsInstance(Env.get("TEST_LIST"), list)
        self.assertIsInstance(Env.get("TEST_DICT"), dict)
        self.assertIsInstance(Env.get("TEST_TUPLE"), tuple)
        self.assertIsInstance(Env.get("TEST_SET"), set)

        # Clean up environment variables after test
        Env.unset("TEST_INT")
        Env.unset("TEST_FLOAT")
        Env.unset("TEST_BOOL")
        Env.unset("TEST_STR")
        Env.unset("TEST_LIST")
        Env.unset("TEST_DICT")
        Env.unset("TEST_TUPLE")
        Env.unset("TEST_SET")