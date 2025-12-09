#!/bin/bash
set -euxo pipefail

SM_SHELL=${SM_SHELL:-js}
SM_FLAGS=${SM_FLAGS:-}

SAMPLY_OPTS=${SAMPLY_OPTS:-}

# To test first-run performance, use the following flags:
# --iteration-count=1 --worst-case-count=0
# IONPERF=func PERF_SPEW_DIR=/tmp samply record $SAMPLY_OPTS $SM_SHELL $SM_FLAGS cli.js $@
IONPERF=ir-graph PERF_SPEW_DIR=/tmp samply record $SAMPLY_OPTS $SM_SHELL $SM_FLAGS cli.js $@
