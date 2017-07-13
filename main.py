#! /usr/bin/env python

import sys
import unittest

from squidsa.parser import Environment, BoardParser
from squidsa.test.runner import SquidsaTextTestRunner


def main(env_name, test_names, skipConnection):
    env = Environment(env_name)
    incomplete_links = env.trim_incomplete_links()

    for l in incomplete_links:
        print("Link {} is not connected to both ends".format(l))

    suite = None
    loader = unittest.TestLoader()
    if test_names:
        for name in test_names:
            pattern = "*{}*.py".format(name)
            if suite is None:
                suite = loader.discover(start_dir="squidsa.test", pattern=pattern)
            else:
                suite.extend(loader.discover(start_dir="squidsa.test", pattern=pattern))
    else:
        suite = loader.discover(start_dir="squidsa.test", pattern="*.py")

    runner = SquidsaTextTestRunner()
    result = runner._makeResult()

    def setupSquidsaEnvironment(test):
        test.env = env

    # setupSquidsaEnvironment is called before a test is started, with the
    # TestCase as parameter. We use that function to inject the environment in
    # the TestCase, thus allowing the TestCase to access information parsed
    # from config files, ssh connection, etc. See SquidaTextTestResult.
    result.setupSquidsaEnvironment = setupSquidsaEnvironment
    result.customFunc = "setupSquidsaEnvironment"

    print("-"*70)

    if not skipConnection:
        env.connect()
    runner.run(suite)
    if not skipConnection:
        env.disconnect()

def usage():
    print("./main.py [environment [test-names]]".format(sys.argv[0]))
    print("./main.py --self-test")
    print()
    print("Execute network tests between a host and a system under test (SUT)")
    print("\tenvironment - name of the config file in conf/env/ (without the cfg extension)")
    print("\ttest-names  - list of python files in test/ (without the py extension) to")
    print("\t              source tests from")

    print("If --self-test is passed, this program will not try to connect to the system")
    print("under test but instead will run tests found in test/sanity.py using the example")
    print("environment")
    print()
    print("Ex: ./main.py zodiac-sfl ping")


if __name__ == "__main__":
    if len(sys.argv) == 1:
            usage()
            sys.exit(0)
    elif len(sys.argv) >= 2:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            usage()
            sys.exit(0)
        elif sys.argv[1] == "--self-test":
            env_name = "env-example"
            test_names = ["sanity", ]
            skipConnection = True
        elif len(sys.argv) == 2:
            env_name = sys.argv[1]
            test_names = None
            skipConnection = False
        else:
            env_name = sys.argv[1]
            test_names = sys.argv[2:]
            skipConnection = False

    main(env_name, test_names, skipConnection)
