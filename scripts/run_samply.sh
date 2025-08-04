#!/bin/bash
set -euo pipefail

TEST=$1

SM_SHELL=${SM_SHELL:-js}
SM_FLAGS=${SM_FLAGS:---enable-ic-frame-pointers --only-inline-selfhosted}

PERF_SPEW_DIR=/tmp IONPERF=ir-ops samply record $SM_SHELL $SM_FLAGS -e "testList = ['$TEST']" cli.js
