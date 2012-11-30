#!/bin/bash

cd $PERF_DIR &&
echo_and_exec "rm -rf build_plots" &&
echo_and_exec "./make_build_plots.sh" &&
echo_and_exec "rsync -rz --delete build_plots mcrl2@www:~/www/performance"
