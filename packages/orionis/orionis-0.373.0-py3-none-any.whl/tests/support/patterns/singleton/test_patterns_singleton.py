from orionis.support.patterns.singleton import Singleton
from orionis.test.cases.asynchronous import AsyncTestCase

class TestPatternsSingleton(AsyncTestCase):
    """
    Test cases for the Singleton metaclass.

    This class contains asynchronous test methods to verify the correct behavior
    of the Singleton metaclass, ensuring that only one instance of a class is created.
    """

    async def testSingleton(self):
        """
        Test the Singleton metaclass.

        Ensures that only one instance of a class using the Singleton metaclass is created,
        regardless of how many times the class is instantiated.
        """
        class SingletonClass(metaclass=Singleton):
            def __init__(self, value):
                self.value = value

        instance1 = SingletonClass(1)
        instance2 = SingletonClass(2)

        self.assertIs(instance1, instance2)
        self.assertEqual(instance1.value, 1)