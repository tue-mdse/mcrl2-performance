#!/bin/bash

# Percentage of physical memory that can maximally be used by the
# performance script
MEM_PERC="90"

# Restrict virtual memory to prevent swapping
MEMORY=`free -k | grep Mem: | sed -e "s/Mem:[ ]*\([0-9]*\).*/\1/"`
MEMLIMIT=`echo "scale=5; ($MEM_PERC/100)*$MEMORY" | bc | sed -e "s/\.[0-9]*//"`
STACKLIMIT=32768

echo -e "\nVirtual memory limit: $MEMLIMIT"
ulimit -S -v $MEMLIMIT
echo -e "\nStack limit: $STACKLIMIT"
ulimit -s $STACKLIMIT

cd $PERF_DIR &&
echo_and_exec "which mcrl22lps" &&
LC_TIME="" date +"%-d %B %Y" > date &&
echo_and_exec "./performance.py"

EXIT_STATUS=$?

# Remove virtual memory limit
ulimit -S -v unlimited

if [ "$EXIT_STATUS" -eq "0" ]; then
  echo_and_exec "rm -rf plots measurements" &&
  echo_and_exec "./make_plots.sh" &&
  echo_and_exec "rsync -rz --delete date revision plots mcrl2@www:~/www/performance/"
fi
