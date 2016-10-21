#!/bin/bash
# Take photos, rsync them to a remote server, and delete old ones.
set -e
# Where is this file installed?
TIMELAPSE_DIR=/home/pi/timelapse

# To run automatically, run
#   crontab -e
# and add (adjusting the path)
#   */10 * * * * /home/pi/timelapse/capture_and_upload.sh

# To disable the Pi camera's LED, reboot after running
#  sudo sh -c 'echo disable_camera_led=1 >> /boot/config.txt'

# Project specific details. This file is expected to define:
#   PROJECT: name used for local and remote subdirectories.
#   REMOTE_PATH: user@host:path to sync files to. (To recreate project/
#       subdirectories under $REMOTE_PATH, it should not have a trailing slash
#       and should not include the project subdirectory.)
# and optionally
#   LOCATION: either a city name or a lat/lng pair as '40.02 -115.78'. If given,
#       switch the camera to night mode for pictures when the sun is down.
#       Requires PyEphem (sudo pip install ephem).
#   PAUSE: if non-empty, skip syncing to the REMOTE_PATH.
#   RASPISTILL_OPTS: extra flags passed to the raspistill command, for example
#       "--hflip --vflip".
source $TIMELAPSE_DIR/project.sh

IMG_DIR=$TIMELAPSE_DIR/$PROJECT/`date -u +%Y`/`date -u +%m`/`date -u +%d`
mkdir -p $IMG_DIR

# Check disk usage and delete old images if free space is getting low.
function check_used()
{
  USED_PERCENT=`df -h $IMG_DIR | tail -1 | sed 's/.*\s\([0-9]\+\)%.*/\1/g'`
}
check_used
while [ $USED_PERCENT -ge 85 ]
do
  OLDEST=`ls -t $TIMELAPSE_DIR/$PROJECT/*/*/*/* | tail -1`
  rm $OLDEST
  check_used
done

if [ -n "${LOCATION}" ]
then
  if $TIMELAPSE_DIR/is_night.py "$LOCATION"
  then
    NIGHT_MODE="--exposure night"
  fi
fi

IMG=${IMG_DIR}/`date -u +%H_%M_%S`.jpg
raspistill --output $IMG --quality 85 $RASPISTILL_OPTS $NIGHT_MODE

# To set up SSH keys for rsyncing without a password prompt, see:
# https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2
if [ -z "$PAUSE" ]
then
  if ! flock -n rsync.lock \
      rsync --archive --recursive $TIMELAPSE_DIR/$PROJECT $REMOTE_PATH
  then
    echo different rsync already in progress after taking $IMG
  fi
else
  echo PAUSEd, skipping sync
fi
