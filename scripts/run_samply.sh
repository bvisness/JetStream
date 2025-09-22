#!/bin/bash
set -euxo pipefail

SM_SHELL=${SM_SHELL:-js}
SM_FLAGS=${SM_FLAGS:-}

# For quicker runs, you may wish to use the following flags:
# --iteration-count=2 --worst-case-count=1
IONPERF=ir-graph PERF_SPEW_DIR=/tmp samply record $SM_SHELL $SM_FLAGS cli.js $@
