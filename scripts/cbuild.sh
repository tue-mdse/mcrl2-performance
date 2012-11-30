#!/bin/bash

# This script may return the following exit codes:
#   0:  building and installing toolset succeeded
#   1:  building toolset succeeded, installing failed
#   2:  building toolset failed

# Location where a temporary backup of the current mCRL2 installation
# will be stored
INSTALL_DIR_TMP=`mktemp -d -u`

# Function for exiting the script when an error has occurred
# Parameter 1: exit code to return
function exit_error {
  # Restore old installation
  rm -rf $INSTALL_DIR
  mv $INSTALL_DIR_TMP $INSTALL_DIR
  exit $1
}

# Backup old installation
mv $INSTALL_DIR $INSTALL_DIR_TMP

# Location of working copy of mCRL2 trunk repository for CMake build
CMAKE_SOURCE_DIR=$SOURCE_DIR/trunk

CMAKE_EXE=/home/mcrl2/cmake-2.8.3-Linux-i386/bin/cmake

# IMPORTANT: We assume that the mCRL2 source tree has already been
# updated to the proper SVN revision.

# Output some environment info for debugging purposes
echo_and_exec "env"

echo ""
echo "which cmake         : `which $CMAKE_EXE`"
echo "cmake --version     : `$CMAKE_EXE --version`"
echo "which gcc           : `which gcc`"
echo "gcc --version       : `gcc --version | head -n 1`"
echo "which wx-config     : `which wx-config`"
echo "wx-config --version : `wx-config --version`"
echo "wx-config --libs    : `wx-config --libs`"

echo_and_exec "rm -rf $CMAKE_BUILD_DIR && mkdir $CMAKE_BUILD_DIR" &&
cd $CMAKE_BUILD_DIR &&
echo_and_exec "$CMAKE_EXE $CMAKE_SOURCE_DIR -DBOOST_ROOT:PATH="/scratch/boost_1_44_0" -DBoost_USE_MULTITHREADED=off -DMCRL2_MAN_PAGES=off -DCMAKE_COLOR_MAKEFILE=off -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR -DMCRL2_ENABLE_EXPERIMENTAL=ON -DMCRL2_ENABLE_DEPRECATED=ON" &&
echo_and_exec "LANG=\"\" time -f \"TIME: %U+%S\" make"

if [ "$?" -ne 0 ] ; then
  exit_error 2
fi

echo_and_exec "make install"

if [ "$?" -ne "0" ]; then
  exit_error 1
fi

# Install succeeded, remove backup of old installation
rm -rf $INSTALL_DIR_TMP

