#! /usr/bin/env python
#
# Startup from system-wide installation

import os
import sys
import argparse
import logging
import unittest

from dsatest.bench import bench
from dsatest import settings
from dsatest import tests as our_tests

logger = logging.getLogger('dsatest')

def setup_logger(verbosity):
    level = 0
    if verbosity == 0:
        level = logging.WARN
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logger.setLevel(level)

    formatter = logging.Formatter('%(levelname)s: %(message)s')

    ch = logging.StreamHandler(stream=sys.stderr)
    ch.setFormatter(formatter)

    logger.addHandler(ch)

def pretty_print_test_suite(suite):
    for t in suite:
        if isinstance(t, unittest.TestCase):
            print(t)
        else:
            pretty_print_test_suite(t)

def recurse_iter_suite(suite, match, patterns):
    for testcase in suite:
        if isinstance(testcase, unittest.TestCase):
            if any(testcase._testMethodName.startswith(p) for p in patterns):
                match.addTest(testcase)
        else:
            recurse_iter_suite(testcase, match, patterns)

def __create_test_suite(test_dir, tests):
    """
    Create a test suite that contains only tests who have names starting with
    test_TEST, TEST being any element in the list "tests".
    """
    loader = unittest.TestLoader()

    # right-strip whitespaces and slashes, so that start_dir
    # and top_level_dir returns the same thing if /foo/bar/ or
    # /foo/bar is passed to this function
    stripped_test_dir = test_dir.rstrip(" /")
    start_dir = stripped_test_dir
    top_level_dir = os.path.dirname(stripped_test_dir)

    if not start_dir or not top_level_dir:
        raise ValueError("Invalid test directory '{}'. Aborting.".format(test_dir))

    if not tests:
        return loader.discover(start_dir=start_dir, top_level_dir=top_level_dir, pattern="*.py")

    # load every tests we can find and do some matching based on that
    suite = loader.discover(start_dir=start_dir, top_level_dir=top_level_dir, pattern="*.py")
    matching_suite = unittest.TestSuite()
    patterns = ["test_{}".format(t) for t in tests]
    recurse_iter_suite(suite, matching_suite, patterns)

    return matching_suite


def create_test_suite(test_dir, test):
    try:
        return __create_test_suite(test_dir, test)
    except Exception:
        print("ERR: Unable to load test directory '{}'. Aborting.".format(test_dir))
        print("ERR: Make sure it's an importable python package (contains __init__.py)")
        sys.exit(1)


def start_bench(bench_conf, test_dir, test_name, list_tests, dry_run):
    bench.setup(bench_conf)
    bench.set_dry_run(dry_run)
    incomplete_links = bench.incomplete_links

    for incomplete_link in incomplete_links:
        logger.warning("Link %s is not connected to both ends", incomplete_link)

    logger.info("Creating test suite. Searching for '%s' in '%s'", test_name, test_dir)
    suite = create_test_suite(test_dir, test_name)
    logger.info("Found %d tests", suite.countTestCases())

    if list_tests:
        if suite.countTestCases() == 0:
            print("No tests found")
        else:
            pretty_print_test_suite(suite)
        sys.exit(0)

    runner = unittest.TextTestRunner(stream=sys.stdout)

    print("-"*70)

    bench.connect()
    result = runner.run(suite)
    bench.disconnect()

    # cumulate tests which raised unexpected exceptions
    # and tests that hadfailed assert methods
    tests_failed = len(result.errors) + len(result.failures)

    return tests_failed


def main():
    test_dir = os.path.dirname(our_tests.__file__)

    parser = argparse.ArgumentParser(description='Control a DSA test bench')
    parser.add_argument('-t', '--test', action='append', default=list(),
                        help="pick only tests whose names start with test_TEST, \
                                this option might be passed several times")
    parser.add_argument('-l', '--list', action='store_true',
                        help="list tests instead of executing them")
    parser.add_argument('-T', '--test-dir', default=test_dir,
                        help="test folder, default to dsatest's test folder")
    parser.add_argument('-B', '--bench', default="bench.cfg",
                        help="bench configuration file")
    parser.add_argument('-C', '--conf-dir', default=None,
                        help='path to the configuration directory')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Skip connection to the test bench (no SSHing is done)')
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    verbosity = args.verbose or 0
    setup_logger(verbosity)

    if args.conf_dir is not None:
        path = os.path.join(os.getcwd(), args.conf_dir)
        settings.set_option(settings.CONF_PATH, os.path.realpath(path))

    bench_cfg = os.path.join(os.getcwd(), args.bench)

    return start_bench(bench_cfg, args.test_dir, args.test, args.list, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
