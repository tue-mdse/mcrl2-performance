#!/bin/bash

# Set umask to ensure that any created file/directory will have group
# write permissions
umask 002

scriptdir=`dirname "$0"`

# Include global configuration
source "${scriptdir}/set_environment.sh"

cd ${SOURCE_DIR}

# Clean and update the local SVN tree
#cd ..
echo_and_exec "svn update --non-interactive" >> $LOG_FILE 2>&1

if [ "$?" -ne "0" ] ; then
  send_email "svn" "${REV_OLD}_${LOG_BASEFILE%.log}"
  exit
fi
upload_log_file "build" $LOG_FILE

# Get the revision number of the updated SVN tree
REV_NEW=`svnversion`

# Print revision numbers
echo "" >> $LOG_FILE
echo "SVN revision of currently installed toolset: $REV_CUR" >> $LOG_FILE
echo "SVN revision of working copy before update: $REV_OLD" >> $LOG_FILE
echo "SVN revision of working copy after update: $REV_NEW" >> $LOG_FILE

# Do nothing if revision has not changed.
# We need to compare REV_CUR and REV_NEW here, not REV_OLD and REV_NEW.
# It can be that REV_OLD==REV_NEW, while REV_CUR < REV_NEW. This happens
# when the performance script was running the previous time this script
# was executed (which prevents installation of a new toolset), and no
# SVN commits have been done in the meantime.
if [ "$REV_CUR" == "$REV_NEW" ] ; then
  echo "Latest SVN revision is already installed; exiting" >> $LOG_FILE
  exit
fi

# Prepend base filename for logs with revision number $REV_NEW
LOG_BASEFILE=${REV_NEW}_$LOG_BASEFILE
if [ "$REV_OLD" != "$REV_NEW" ] ; then
  # Rename log file we used so far
  mv $LOG_FILE $LOG_DIR/build/$LOG_BASEFILE
fi

# List of jobs to be done
#JOBS=( backup libdoc ) disabled libdoc 10/2/2012 JK
JOBS=( backup )

# Only attempt to compile and install the toolset if the performance
# script is not running
if ! ps ax | grep -v grep | grep performance.py &> /dev/null ; then
# Old line: JOBS=( ${JOBS[@]:0} build )
  JOBS=( ${JOBS[@]:0} cbuild )
fi

I=0
while [ "$I" -lt "${#JOBS[*]}" ] ; do
  j="${JOBS[$I]}"
  echo "executing job $j"
  LOG_FILE=$LOG_DIR/$j/$LOG_BASEFILE

  #-- uncomment this to skip performance task
  #if [ "$j" == "performance" ] ; then
  #  let "I++"
  #  continue
  #fi

  # Execute the job
  ( time $SCRIPTS_DIR/$j.sh ) 2>&1 | tee -a $LOG_FILE

  #EXIT_STATUS=$?
  # $? returns the exit status of tee, so we apply a workaround
  # see http://www.unix.com/shell-programming-scripting/92163-command-does-not-return-exit-status-due-tee.html
  # for more details
  EXIT_STATUS=${PIPESTATUS[0]}

  if [ "$j" == "performance" -o "$j" == "cbuild" -o "$j" == "build" ] ; then
    upload_log_file "$j" $LOG_FILE

    if [ "$EXIT_STATUS" -ne "0" ] ; then
      send_email "$j" "${LOG_BASEFILE%.log}"
    fi
  fi

  if [ "$j" == "cbuild" -a "$EXIT_STATUS" -lt "2" ] ; then
    # Building the toolset succeeded, store the build time
    TM=`grep "TIME:" $LOG_FILE | sed -e "s/TIME: //" | bc`
    echo -e "$REV_NEW\t$TM" >> $PERF_DIR/build_data/$j.perf

    # Also upload build plots
    JOBS=( ${JOBS[@]:0} build_plots )

    if [ "$EXIT_STATUS" -eq "0" ] ; then
      # Installing the toolset succeeded as well, so we also upload
      # source package and measure tool performance
      # Furthermore, we generate the sphinx documentation
      JOBS=( ${JOBS[@]:0} performance )
    fi
  fi

  if [ "$j" == "cbuild" -a "$EXIT_STATUS" -eq "0" ] ; then
    # CMake build succeeded, store the build time
    TM=`grep -P "TIME: \d" $LOG_FILE`
    if [ "$?" == "0" ] ; then
      TM=`echo $TM | sed -e "s/TIME: //" | bc`
      echo -e "$REV_NEW\t$TM" >> $PERF_DIR/build_data/$j.perf
    fi
  fi

  let "I++"
done
