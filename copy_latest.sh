#!/bin/bash
# Install with crontab -e
#   3,13,23,33,43,53 * * * * /home/timelapse/timelapse/copy_latest.sh
# offset from Pi upload time.

SRC=/mnt/data/timelapse
DST=~/public_html

for project in `ls $SRC`
do
  if [ $project = 'var' -o $project = 'archive' ]
  then
    continue
  fi
  LATEST=`ls -1 $SRC/$project/*/*/*/* | tail -1`
  mkdir -p $DST/$project
  # sudo apt-get install imagemagick
  width=`identify -format %W $LATEST`
  convert \
      -background '#0008' -fill white \
      -gravity west -size ${width}x30 \
      caption:"$LATEST" \
      $LATEST \
      +swap \
      -gravity south \
      -composite \
      $DST/$project/latest.jpg
done
