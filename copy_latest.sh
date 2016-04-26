#!/bin/bash
# Install with crontab -e
#   3,13,23,33,43,53 * * * * /home/timelapse/timelapse/copy_latest.sh
# offset from Pi upload time.

SRC=/mnt/data/timelapse
DST=~/public_html

# sudo apt-get install imagemagick
MONTAGE=`which montage`

for project in `ls $SRC`
do
  LATEST=`ls -1 $SRC/$project/*/*/*/* | tail -1`
  mkdir -p $DST/$project
  if [ -n "$MONTAGE" ]
  then
    $MONTAGE -background black -fill white \
        -geometry +0+0 -label "$LATEST" -pointsize 24 \
        $LATEST $DST/$project/latest.jpg
  else
    cp $LATEST $DST/$project/latest.jpg
  fi
done
