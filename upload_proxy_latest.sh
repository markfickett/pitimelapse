#!/bin/bash
# Upload a proxy resolution version of the latest image.
# For example, run this as a daily cron (09:05, local time zone):
# 5 9 * * * /home/pi/timelapse/upload_proxy_latest.sh
set -e

TIMELAPSE_DIR=/home/pi/timelapse
PROXY_SIZE=1296

# See capture_and_upload.sh docs for project.sh.
source $TIMELAPSE_DIR/project.sh

newest=`ls $TIMELAPSE_DIR/$PROJECT/*/*/*/* | tail -1`
tmp_file=`mktemp -t pitimelapse.XXXXXX`
# sudo apt-get install imagemagick
convert \
    -resize ${PROXY_SIZE}x${PROXY_SIZE} \
    $newest \
    $tmp_file
proxy_name=`echo ${newest#$TIMELAPSE_DIR/$PROJECT/} | tr '/' '_'`
# Use `ssh user@host 'mkdir -p path` for first-time setup.
scp $tmp_file ${REMOTE_PATH}/${PROJECT}_${PROXY_SIZE}/$proxy_name
rm $tmp_file
