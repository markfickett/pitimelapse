#!/usr/bin/env python3
"""Deletes images taken while the sun is down from a project directory."""

import argparse
import logging
import os
import ephem  # sudo pip install ephem

import main_util
import project

# Allow for slightly below the horizon, to keep dawn/dusk images.
_FULL_DARK_ALTITUDE = -0.15


def RemoveNightImages(project_dir, lat_str, lon_str, dry_run):
  """Deletes all timestamped images in taken when the sun was down."""
  observer = ephem.Observer()
  observer.lat = lat_str
  observer.lon = lon_str
  sun = ephem.Sun()

  n_files = 0
  n_night = 0

  for filename in project.IterProject(project_dir, reverse=False):
    n_files += 1
    _, timestamp = project.GetFlatFileNameAndTime(filename)
    observer.date = ephem.Date(timestamp)
    sun.compute(observer)
    is_night = sun.alt < _FULL_DARK_ALTITUDE
    logging.info(
        '%s\tsun alt %f\t%s'
        % (filename, sun.alt, 'night' if is_night else 'day'))
    if is_night:
      n_night += 1
      if not dry_run:
        os.remove(filename)

  logging.info(
      '%d files, %d night (%sremoved), remaining %d day'
      % (n_files, n_night, 'would be ' if dry_run else '', n_files - n_night))

if __name__ == '__main__':
  main_util.ConfigureLogging()

  parser = argparse.ArgumentParser()
  parser.add_argument(
      'project_dir',
      help='Project directory containing timestamped images or subfolders.')
  parser.add_argument(
      'lat', help='Camera location decimal latitude, for example 42.01.')
  parser.add_argument(
      'lon', help='Camera location decimal longitude, for example -72.99.')
  parser.add_argument(
      '--dry_run',
      action='store_true',
      help='If true, do not remove any files.')
  args = parser.parse_args()

  RemoveNightImages(args.project_dir, args.lat, args.lon, args.dry_run)
