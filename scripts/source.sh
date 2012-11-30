#!/bin/bash

# IMPORTANT: We assume that the mCRL2 source tree has already been
# updated to the proper SVN revision.

SRC_PATTERN="mcrl2*.tar.gz"

cd $CMAKE_BUILD_DIR &&
echo_and_exec "make package_source" &&
echo_and_exec "ssh mcrl2@www \"rm -f ~/www/download/devel/$SRC_PATTERN\"" &&
echo_and_exec "rsync -rz ${CMAKE_BUILD_DIR}/mcrl2-*.tar.gz mcrl2@www:~/www/download/devel"

