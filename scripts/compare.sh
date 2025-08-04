# #!/bin/bash
set -euo pipefail

TEST=$1
JETSTREAM_DIR=$(pwd)

SM_SHELL=${SM_SHELL:-js}
V8_SHELL=${V8_SHELL:-v8} # jsvu installs a shell called "v8"; a build from source will be called "d8"

echo "---------------- $TEST ----------------"

export IONPERF=ir
export PERF_SPEW_DIR=/tmp
SM_OPTS="--only-inline-selfhosted --emit-interpreter-entry --enable-ic-frame-pointers --async-stacks-capture-debuggee-only"
samply record --save-only -o sm-perf.data -r 10000 $SM_SHELL $SM_OPTS -e "testList = ['$TEST']" cli.js

V8_OPTS="--perf-prof --interpreted-frames-native-stack --allow-natives-syntax --no-turbo-inlining --no-maglev-inlining"
samply record --save-only -o v8-perf.data -r 10000 $V8_SHELL $V8_OPTS -e "testList = ['$TEST']" cli.js

(samply load --no-open sm-perf.data > /tmp/sm.txt) &
(samply load --no-open v8-perf.data > /tmp/v8.txt) &

# Give samply a second to settle
sleep 1

sm_url=$(cat /tmp/sm.txt)
v8_url=$(cat /tmp/v8.txt)

cd comparison-report-generator

yarn
yarn playwright install
yarn generate-report $TEST \
  --reference-profile $sm_url --reference-name "SM" \
  --alternative-profile $v8_url --alternative-name "v8" \
  --base-path=$JETSTREAM_DIR

killall samply
