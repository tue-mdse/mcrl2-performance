#!/bin/bash

# Global configuration settings for the mCRL2 cronjob scripts

# Do not use compiler cache!
export CCACHE_DISABLE=1

# Top level directory for mCRL2 cronjobs
export MCRL2CRON_DIR=/scratch/mcrl2-cron2

# Location of cronjob scripts
export SCRIPTS_DIR=$MCRL2CRON_DIR/scripts

# Location of local mCRL2 SVN source tree
export SOURCE_DIR=$MCRL2CRON_DIR/svn

# Location of performance data
export PERF_DIR=$MCRL2CRON_DIR/performance

# Location of local mCRL2 installation
export INSTALL_DIR=$MCRL2CRON_DIR/install

# Location of CMake build
export CMAKE_BUILD_DIR=$MCRL2CRON_DIR/cbuild

# Base path to log-directories
LOG_DIR=$MCRL2CRON_DIR/logs

# Add paths to important tools
export PATH=$INSTALL_DIR/bin:$PATH
export LD_LIBRARY_PATH=$INSTALL_DIR/lib/mcrl2:$LD_LIBRARY_PATH

# Function for echoing and executing a command
function echo_and_exec {
  echo -e "\n[`pwd`]\$ $1"
  /bin/bash -c "$1"
}
export -f echo_and_exec

# Base filename for every log-file (will be prepended with SVN revision
# number below)
LOG_BASEFILE="`LC_TIME="" date +"%F_%H.%M"`.log"

# E-mail address to notify if anything fails
TO_EMAIL="mcrl2-development@listserver.tue.nl"
# E-mail address that appears in the From field
# Note that if $TO_EMAIL is a mailing list, $FROM_EMAIL must have
# permission to post messages on that mailing list!
FROM_EMAIL="mcrl2-cron@win.tue.nl"

# Function for uploading a log file
# Parameter 1: job that was running
# Parameter 2: log file name
function upload_log_file {
  scp $2 mcrl2@www:~/www/performance/logs/$1
}

# Function for sending an e-mail message
# Parameter 1: job that was running
# Parameter 2: base name of log file
function send_email {
  LOG_TYPE="$1"
  SUBJECT="$1"
  if [ "$1" == "performance" ] ; then
    SUBJECT="Performance measurements"
#  elif [ "$1" == "build" ] ; then
#    SUBJECT="Toolset build (bjam)"
  elif [ "$1" == "cbuild" ] ; then
    SUBJECT="Toolset build (cmake)"
  elif [ "$1" == "svn" ] ; then
    SUBJECT="SVN update"
    LOG_TYPE="build"
  fi
  SUBJECT="$SUBJECT failed on $HOSTNAME"
  echo "$SUBJECT.
The log can be viewed at:
http://www.mcrl2.org/performance/logs.php?log=$2&type=$LOG_TYPE" |
  mail -r $FROM_EMAIL -s "$SUBJECT" $TO_EMAIL
}

cd $SOURCE_DIR

# Get the revision number of the currently installed toolset
REV_CUR=0
if which mcrl22lps &> /dev/null ; then
#  REV_CUR=`mcrl22lps --version | grep revision | sed -e "s/.*revision \([0-9]*\).*/\1/"`
# The previous used an old versioning scheme
  REV_CUR=`mcrl22lps --version | head -n1 | sed -e "s/.*[0-9]*\.[0-9]*\.\([0-9]*\).*/\1/"`
fi

# Get the revision number of the current SVN tree
REV_OLD=`svnversion`

LOG_FILE=$LOG_DIR/build/${REV_OLD}_$LOG_BASEFILE

