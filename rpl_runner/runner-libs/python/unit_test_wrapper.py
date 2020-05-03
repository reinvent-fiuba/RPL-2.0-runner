import json
import os
import unittest

import unit_test  # module implemented by the teacher with the activitie's unit tests


# We implement our own TestResult class so that we can then present UnitTest results however we want
# See available overridable methods here https://docs.python.org/3.4/library/unittest.html#unittest.TestResult

class RplTestResult(unittest.TestResult):

    def __init__(self, stream=None, descriptions=None, verbosity=None):
        super().__init__(stream, descriptions, verbosity)
        self.passed = []

    def addSuccess(self, test):
        self.passed.append(test)
        super().addSuccess(test)

    def stopTestRun(self):
        tests = [{"name": test._testMethodName, "status": "PASSED", "messages": None} for test in self.passed]

        tests.extend([{"name": test._testMethodName, "status": "FAILED", "messages": exception} for test, exception in
                      self.failures])

        tests.extend([{"name": test._testMethodName, "status": "ERROR", "messages": exception} for test, exception in
                      self.errors])

        tests.extend([{"name": test._testMethodName, "status": "SKIPPED", "messages": reason} for test, reason in
                      self.skipped])

        result = {
            "passed": len(self.passed),
            "failed": len(self.failures),
            "errored": len(self.errors),
            'tests': tests
        }

        # print(json.dumps(result, indent=4))

        with open("unit_test_results_output.json", "w") as of:
            of.write(json.dumps(result, indent=4))

        super().stopTestRun()


if __name__ == '__main__':
    nullf = open(os.devnull, 'w')

    testToRun = unittest.TextTestRunner(stream=nullf, descriptions=True,
                                        verbosity=2, failfast=False, buffer=False,
                                        resultclass=RplTestResult)
    suite = unittest.TestLoader().loadTestsFromTestCase(unit_test.TestMethods)
    testToRun.run(suite)
