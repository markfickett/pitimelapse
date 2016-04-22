#!/bin/bash
set -e
# Where is this file installed?
TIMELAPSE_DIR=/home/pi/timelapse

# To run automatically, run
#   crontab -e
# and add (adjusting the path)
#   */10 * * * * /home/pi/timelapse/capture_and_upload.sh

# Project specific details. This file is expected to define:
#   PROJECT: name used for local and remote subdirectories.
#   REMOTE_PATH: user@host:path to sync files to. (To recreate project/
#       subdirectories under $REMOTE_PATH, it should not have a trailing slash
#       and should not include the project subdirectory.)
source $TIMELAPSE_DIR/project.sh

IMG_DIR=$TIMELAPSE_DIR/$PROJECT/`date -u +%Y`/`date -u +%m`/`date -u +%d`

mkdir -p $IMG_DIR
raspistill \
  --output ${IMG_DIR}/`date -u +%H_%M_%S`.jpg \
  --quality 85

rsync --archive --recursive $TIMELAPSE_DIR/$PROJECT $REMOTE_PATH
