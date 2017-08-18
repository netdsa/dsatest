#! /bin/sh
#
# A small wrapper to inject the current folder in PYTHONPATH
# and start the right executable

SQUIDSA_REALPATH=$(dirname $(realpath $0))
SQUIDSA_PARENT_REALPATH=$(dirname ${SQUIDSA_REALPATH})

PYTHONPATH=${SQUIDSA_PARENT_REALPATH} ${SQUIDSA_REALPATH}/bin/bench $@
