#!/bin/bash

# Install sphinx using easy_install --user sphinx

echo_and_exec "which mcrl22lps"

cd $CMAKE_BUILD_DIR &&
echo_and_exec "make doc" &&
echo_and_exec "rsync -rz --delete doc/sphinx/html/* mcrl2@www:~/www/dev"

