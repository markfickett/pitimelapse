#!/usr/bin/env python
"""Upload a proxy resolution version of the latest image.

For example, run this as a daily cron (09:05, local time zone):
5 9 * * * /home/pi/timelapse/upload_proxy_latest.py
"""
import logging
import os
import subprocess

from main_util import ConfigureLogging
from project import GetProjectLatest
from project import GetFlatFileNameAndTime


# FIXME From command-line args or project.sh or equivalent.
IMG_BASE = '/media/pi/SHORT128/timelapse/green-acres-west/'
PROXY_SIZE=1296
REMOTE_PATH='timelapse@naib.markfickett.com:/mnt/data/timelapse/'
PROJECT='green-acres-west'


def upload_proxy_latest():
  latest = GetProjectLatest(IMG_BASE)
  if latest is None:
    raise RuntimeError('No file found in project %r.' % IMG_BASE)
  flat_file_name, unused_timestamp = GetFlatFileNameAndTime(latest)

  # TODO something like `mktemp -t pitimelapse.XXXXXX`
  tmp_file_name = '/tmp/pitimelapse-proxy.jpg'

  # sudo apt-get install imagemagick
  subprocess.check_call([
    'convert',
    '-resize', '%dx%d' % (PROXY_SIZE, PROXY_SIZE),
    latest,
    tmp_file_name,
  ])

  # We want to construct a path for the remote host's OS. The path.join here
  # will probably work, but a '/'.join may actually be more correct.
  remote_path = os.path.join(
      REMOTE_PATH, '%s_%d' % (PROJECT, PROXY_SIZE), flat_file_name)
  logging.info(
      'Uploading %d proxy of %r to %r.', PROXY_SIZE, latest, remote_path)
  # Use `ssh user@host 'mkdir -p path` for first-time setup.
  subprocess.check_call([
    'scp',
    tmp_file_name,
    remote_path,
  ])
  os.unlink(tmp_file_name)


if __name__ == '__main__':
  ConfigureLogging()
  upload_proxy_latest()
