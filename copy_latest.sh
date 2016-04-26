#!/bin/bash
# Install with crontab -e
#   3,13,23,33,43,53 * * * * /home/timelapse/timelapse/copy_latest.sh
# offset from Pi upload time.

SRC=/mnt/data/timelapse
DST=~/public_html

for project in `ls $SRC`
do
  LATEST=`ls -1 $SRC/$project/*/*/*/* | tail -1`
  mkdir -p $DST/$project
  cp $LATEST $DST/$project/latest.jpg
done
