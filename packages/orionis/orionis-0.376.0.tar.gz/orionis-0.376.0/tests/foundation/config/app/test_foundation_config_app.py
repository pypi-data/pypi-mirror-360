from orionis.foundation.config.app.entities.app import App
from orionis.foundation.config.app.enums.ciphers import Cipher
from orionis.foundation.config.app.enums.environments import Environments
from orionis.foundation.exceptions.integrity import OrionisIntegrityException
from orionis.test.cases.asynchronous import AsyncTestCase

class TestFoundationConfigApp(AsyncTestCase):

    async def testDefaultValues(self):
        """
        Test that the App instance is created with the correct default values.

        Notes
        -----
        Verifies that all default values match the expected defaults from the class definition.
        """
        app = App()
        self.assertEqual(app.name, 'Orionis Application')
        self.assertEqual(app.env, Environments.DEVELOPMENT.value)
        self.assertTrue(app.debug)
        self.assertEqual(app.url, 'http://127.0.0.1')
        self.assertEqual(app.port, 8000)
        self.assertEqual(app.timezone, 'UTC')
        self.assertEqual(app.locale, 'en')
        self.assertEqual(app.fallback_locale, 'en')
        self.assertEqual(app.cipher, Cipher.AES_256_CBC.value)
        self.assertIsNone(app.key)
        self.assertEqual(app.maintenance, '/maintenance')

    async def testEnvironmentValidation(self):
        """
        Test that the environment attribute is properly validated and converted.

        Notes
        -----
        Verifies that string environments are converted to enum values and invalid environments raise exceptions.
        """
        # Test valid string environment
        app = App(env="PRODUCTION")
        self.assertEqual(app.env, Environments.PRODUCTION.value)

        # Test valid enum environment
        app = App(env=Environments.TESTING)
        self.assertEqual(app.env, Environments.TESTING.value)

        # Test invalid environment
        with self.assertRaises(OrionisIntegrityException):
            App(env="INVALID_ENV")

    async def testCipherValidation(self):
        """
        Test that the cipher attribute is properly validated and converted.

        Notes
        -----
        Verifies that string ciphers are converted to enum values and invalid ciphers raise exceptions.
        """
        # Test valid string cipher
        app = App(cipher="AES_128_CBC")
        self.assertEqual(app.cipher, Cipher.AES_128_CBC.value)

        # Test valid enum cipher
        app = App(cipher=Cipher.AES_192_CBC)
        self.assertEqual(app.cipher, Cipher.AES_192_CBC.value)

        # Test invalid cipher
        with self.assertRaises(OrionisIntegrityException):
            App(cipher="INVALID_CIPHER")

    async def testTypeValidation(self):
        """
        Test that type validation works correctly for all attributes.

        Notes
        -----
        Verifies that invalid types for each attribute raise OrionisIntegrityException.
        """
        # Test invalid name type
        with self.assertRaises(OrionisIntegrityException):
            App(name=123)

        # Test invalid debug type
        with self.assertRaises(OrionisIntegrityException):
            App(debug="true")

        # Test invalid url type
        with self.assertRaises(OrionisIntegrityException):
            App(url=123)

        # Test invalid port type
        with self.assertRaises(OrionisIntegrityException):
            App(port="8000")

        # Test invalid workers type
        with self.assertRaises(OrionisIntegrityException):
            App(workers="4")

        # Test invalid reload type
        with self.assertRaises(OrionisIntegrityException):
            App(reload="true")

    async def testToDictMethod(self):
        """
        Test that the toDict method returns a proper dictionary representation.

        Notes
        -----
        Verifies that the returned dictionary contains all expected keys and values.
        """
        app = App()
        app_dict = app.toDict()

        self.assertIsInstance(app_dict, dict)
        self.assertEqual(app_dict['name'], 'Orionis Application')
        self.assertEqual(app_dict['env'], Environments.DEVELOPMENT.value)
        self.assertTrue(app_dict['debug'])
        self.assertEqual(app_dict['url'], 'http://127.0.0.1')
        self.assertEqual(app_dict['port'], 8000)
        self.assertEqual(app_dict['timezone'], 'UTC')
        self.assertEqual(app_dict['locale'], 'en')
        self.assertEqual(app_dict['fallback_locale'], 'en')
        self.assertEqual(app_dict['cipher'], Cipher.AES_256_CBC.value)
        self.assertIsNone(app_dict['key'])
        self.assertEqual(app_dict['maintenance'], '/maintenance')

    async def testNonEmptyStringValidation(self):
        """
        Test that empty strings are rejected for attributes requiring non-empty strings.

        Notes
        -----
        Verifies that attributes requiring non-empty strings raise exceptions when empty strings are provided.
        """
        with self.assertRaises(OrionisIntegrityException):
            App(name="")

        with self.assertRaises(OrionisIntegrityException):
            App(url="")

        with self.assertRaises(OrionisIntegrityException):
            App(timezone="")

        with self.assertRaises(OrionisIntegrityException):
            App(locale="")

        with self.assertRaises(OrionisIntegrityException):
            App(fallback_locale="")

        with self.assertRaises(OrionisIntegrityException):
            App(maintenance="")