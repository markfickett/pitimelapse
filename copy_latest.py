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

import argparse
import os
import re
import subprocess


SKIP_PROJECTS = (
    'var',
    'archive',
)


def IterProject(project_dir_path, reverse=True):
  filenames = os.listdir(project_dir_path)
  if not filenames:
    return
  if re.match(r'^\d\d\d\d$', filenames[0]):
    # Expect YYYY/MM/DD/HH_MM_SS.ext hierarchy.
    year_dirs = [os.path.join(project_dir_path, f) for f in filenames]
    for year_dir in sorted(year_dirs, reverse=reverse):
      month_dirs = [os.path.join(year_dir, f) for f in os.listdir(year_dir)]
      for month_dir in sorted(month_dirs, reverse=reverse):
        day_dirs = [os.path.join(month_dir, f) for f in os.listdir(month_dir)]
        for day_dir in sorted(day_dirs, reverse=reverse):
          for filename in sorted(os.listdir(day_dir), reverse=reverse):
            yield os.path.join(day_dir, filename)
  else:
    # Expect a flat directory of YYYY_MM_DD_HH_MM_SS.ext files.
    for filename in sorted(filenames, reverse=reverse):
      yield os.path.join(project_dir_path, filename)


def CopyAllLatest(src_dir_path, dst_dir_path):
  for project_dir in os.listdir(src_dir_path):
    if project_dir in SKIP_PROJECTS:
      continue
    CopyLatest(
        os.path.join(src_dir_path, project_dir),
        os.path.join(dst_dir_path, project_dir))


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


def _Expand(raw_path):
  return os.path.abspath(os.path.expanduser(raw_path))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'src',
      help='Project directory, containing either YYYY dirs or flat files.')
  parser.add_argument(
      'dst',
      help='Output directory in which to create project subdir and latest.jpg.')
  args = parser.parse_args()
  CopyAllLatest(_Expand(args.src), _Expand(args.dst))
