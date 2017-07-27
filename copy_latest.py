#!/usr/bin/env python
"""
Copy the latest captured image from each time lapse project to a new location.
Add the original filename as an overlay on the image when copying it. This
copies from each $SRC/$PROJECT directory, creating a new
$DST/$PROJECT/latest.jpg.

Install with crontab -e
    3,13,23,33,43,53 * * * * /home/timelapse/timelapse/copy_latest.py SRC DST
offset from time lapse camera's upload time.
"""

import os
import re
import subprocess

from main_util import ApplyPerProject
from main_util import GetSrcDstParser
from project import IterProject


def CopyLatest(project_src_path, project_latest_dir_path):
  try:
    latest_src_path = iter(
        IterProject(project_src_path, reverse=True)).next()
  except StopIteration:
    return
  if not os.path.isdir(project_latest_dir_path):
    os.makedirs(project_latest_dir_path)
  _, ext = os.path.splitext(latest_src_path)
  latest_dst_path = os.path.join(
      project_latest_dir_path, 'latest' + ext.lower())

  # Run `sudo apt-get install imagemagick` for `identify` and `convert`.
  width_str = subprocess.check_output(
      ['identify', '-format', '%W', latest_src_path])
  width = int(width_str)
  subprocess.check_call([
      'convert',
      '-background', '#0008', '-fill', 'white',
      '-gravity', 'west', '-size', '%dx30' % width,
      'caption:%s' % latest_src_path,
      latest_src_path,
      '+swap',
      '-gravity', 'south',
      '-composite',
      latest_dst_path,
  ])


if __name__ == '__main__':
  parser = GetSrcDstParser()
  args = parser.parse_args()
  ApplyPerProject(args.src, args.dst, CopyLatest)
