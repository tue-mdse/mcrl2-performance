#!/bin/bash
# Backup all precious data and scripts for the mCRL2 cronjobs

cd $MCRL2CRON_DIR

# Files/dirs that will be backed up
FILES='
scripts
performance/build_data
performance/data
performance/*.py
performance/*.sh
performance/*memusage*
performance/revision
performance/plotstyle.plt'

ARCHIVE=mcrl2-cron-backup.tar.bz2 
# Alternative archive name, that includes date and time:
#ARCHIVE=mcrl2-cron-backup-`date +"%Y%m%d_%H%M"`.tar.bz2

# Location where archive will be stored
ARCHIVE_DIR=$HOME/backups

tar -cjf $ARCHIVE $FILES

mv $ARCHIVE $ARCHIVE_DIR
