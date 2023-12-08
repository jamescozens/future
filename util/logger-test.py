import unittest
from os import path
from logger import LOGGING_CONFIG_DEFAULT, getLogger, Level, logMsg, logMe


class SimpleTestCase(unittest.TestCase):
    _logger = None

    def setUp(self):
        """Call before every test case."""
        if not (path.isfile(LOGGING_CONFIG_DEFAULT) and path.exists(LOGGING_CONFIG_DEFAULT)):
            raise FileNotFoundError(f'Cannot find the file: {LOGGING_CONFIG_DEFAULT}')

        self._logger = getLogger(__name__)

        pass

    def tearDown(self):
        """Call after every test case."""

        if (self._logger is None):
            assert False, 'the logger is not defined cannot test'
        else
            args = [123,'abc', ]
            getLogger().   (logMsg())   .log(Level.DEBUG, 'msg', )
            assert False, 'the logger is not defined cannot test'

        pass

    def testA(self):
        """Test case A. note that all test method names must begin with 'test.'"""
        assert True, "bar() not calculating values correctly"

    def testB(self):
        """test case B"""
        assert True, "can't add Foo instances"

    def testC(self):
        """test case C"""
        assert True, "baz() not returning blah correctly"


if __name__ == "__main__":
    unittest.main()  # run all tests
