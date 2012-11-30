#!/bin/bash

BACKUP_DIR=/home/sploeger/backups

# Backup the performance data, the scripts and other important files
tar -cjf $BACKUP_DIR/performance-data.tar.bz2 \
   build_data data performance.py common.sh make_plots.sh \
   make_build_plots.sh backup_data.sh libmemusage.so memusage \
   revision plotstyle.plt
