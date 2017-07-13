
import unittest

class SquidsaTextTestResult(unittest.TextTestResult):
    """
    Modified unittest.TextTestResult that calls a custom function (if it has
    been set) before running the test.

    It is intended to be used in combination with a SquisaTextTestRunner
    instance. So usually, you would use this like this:


    runner = SquidsaTextTestRunner()
    result = runner._makeResult()

    def myCustomFunction(test):
        # do something with test, like adding an attribute
        test.foo = "bar"

    result.setupFooAttribute = myCustomFunction
    result.customFunc = "setupFooAttribute"


    Before each test is run, myCustomFunction will be called. In our context,
    we use that to inject the environment in the test case, so that it can
    access board interfaces etc.
    """

    customFunc = None

    def startTest(self, test):
        super(SquidsaTextTestResult, self).startTest(test)
        if self.customFunc and hasattr(self, self.customFunc):
            getattr(self, self.customFunc)(test)

class SquidsaTextTestRunner(unittest.TextTestRunner):
    """
    Modified unittest.TextTestRunner that caches the value of _makeResult
    """

    resultclass = SquidsaTextTestResult

    def _makeResult(self):
        if not hasattr(self, "mk_result"):
            self.mk_result = self.resultclass(self.stream, self.descriptions, self.verbosity)
        return self.mk_result

