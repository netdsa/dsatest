#! /bin/sh
#
# A small wrapper to inject the current folder in PYTHONPATH
# and start the right executable

DSATEST_REALPATH=$(dirname $(realpath $0))
DSATEST_PARENT_REALPATH=$(dirname ${DSATEST_REALPATH})/dsatest/

PYTHONPATH=${DSATEST_PARENT_REALPATH} ${DSATEST_REALPATH}/bin/dsatest $@
