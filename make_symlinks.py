#!/usr/bin/env python
"""Make hourly/daily/monthly symlinks to images in a flat directory.

Usage: %(prog)s IN_DIR OUT_DIR [--interval HOUR|DAY|MONTH] [--hour] [--day]
"""

import argparse
import datetime
import os


_IGNORE_FILES = set(('.DS_Store', '.', '..'))


class _Interval(object):
  HOUR = 'HOUR'
  DAY = 'DAY'
  MONTH = 'MONTH'


def _parse_interval(value_str):
  return {
    _Interval.HOUR: _Interval.HOUR,
    _Interval.DAY: _Interval.DAY,
    _Interval.MONTH: _Interval.MONTH,
  }[value_str.upper()]


class _Image(object):
  """A relative path to an image, parsed as a timestamp.

  Two formats are available: with multiple subdirectories, or flat (with the
  full timestamp embedded in the filename).
  """
  _TIMESTAMP_ELEMENTS = ['%Y', '%m', '%d', '%H_%M_%S']
  _PATH_TIMESTAMP_PATTERN = os.path.join(*_TIMESTAMP_ELEMENTS)

  def __init__(self, relative_multi_dir_path):
    self._multi_dir_path = relative_multi_dir_path
    path, self._ext = os.path.splitext(relative_multi_dir_path)
    self.dt = datetime.datetime.strptime(path, self._PATH_TIMESTAMP_PATTERN)
    self._flat_path = self.dt.strftime(
        '_'.join(self._TIMESTAMP_ELEMENTS) + self._ext)

  def get_multi_dir_path(self):
    return self._multi_dir_path

  def get_flat_path(self):
    return self._flat_path

  def get_datetime(self):
    return self.dt


def _abspath(path):
  return os.path.normpath(os.path.abspath(os.path.expanduser(path)))


def create_symlinks(raw_src_path, dst_path, interval, hour, day):
  minute = 0
  src_path = _abspath(raw_src_path)
  os.makedirs(dst_path)
  for subdir, unused_dirnames, filenames in os.walk(src_path):
    for filename in filenames:
      if filename in _IGNORE_FILES:
        continue
      full_path = os.path.join(subdir, filename)
      local_path = full_path[len(src_path) + 1:]
      img = _Image(local_path)

      if img.dt.minute != minute:
        continue
      if (interval == _Interval.MONTH and
          not (img.dt.day == day and img.dt.hour == hour)):
        continue
      if (interval == _Interval.DAY and not (img.dt.hour == hour)):
        continue

      os.symlink(full_path, os.path.join(dst_path, img.get_flat_path()))


if __name__ == '__main__':
  parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('src', help='source directory with YYYY/MM/DD/HHMMSS.jpg')
  parser.add_argument('dst', help='Create symlinks in this output directory.')

  parser.add_argument(
      '--interval', type=_parse_interval, default=_Interval.HOUR)

  parser.add_argument('--hour', type=int, default=16)
  parser.add_argument('--day', type=int, default=1)

  args = parser.parse_args()
  create_symlinks(
      args.src, args.dst, args.interval, args.hour, args.day)
