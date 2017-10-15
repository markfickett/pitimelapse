import datetime
import logging
import os
import re


IGNORE_FILES = ('.DS_Store',)


def _list_absolute_paths(src_dir, reverse):
  child_dirs = [
      os.path.join(src_dir, f) for f in os.listdir(src_dir)
      if f not in IGNORE_FILES]
  return sorted(child_dirs, reverse=reverse)


def IterProject(project_dir_path, reverse=True):
  filenames = os.listdir(project_dir_path)
  if not filenames:
    logging.info('%r empty, early-exit project iteration.', project_dir_path)
    return
  if re.match(r'^\d\d\d\d$', filenames[0]):
    # Expect YYYY/MM/DD/HH_MM_SS.ext hierarchy.
    year_dirs = _list_absolute_paths(project_dir_path, reverse)
    for year_dir in year_dirs:
      month_dirs = _list_absolute_paths(year_dir, reverse)
      for month_dir in month_dirs:
        day_dirs = _list_absolute_paths(month_dir, reverse)
        for day_dir in day_dirs:
          for filename in _list_absolute_paths(day_dir, reverse):
            yield filename
  else:
    # Expect a flat directory of YYYY_MM_DD_HH_MM_SS.ext files.
    for filename in sorted(filenames, reverse=reverse):
      if filename in IGNORE_FILES:
        continue
      yield os.path.join(project_dir_path, filename)


def GetProjectLatest(project_src_path):
  try:
    return iter(IterProject(project_src_path, reverse=True)).next()
  except StopIteration:
    return None


def GetFlatFileNameAndTime(flat_or_hierarchical_path):
  """Returns (flat local filename, timestamp from original path or filename)."""
  # If the local filename isn't already flat (containing date as well as time),
  # combine the path hierarchy (which includes the date) with the local name.
  _, local_filename = os.path.split(flat_or_hierarchical_path)
  if re.match(r'\d\d\d\d_.*', local_filename):
    flat_filename = local_filename
  else:
    flat_filename = '_'.join(flat_or_hierarchical_path.split(os.path.sep)[-4:])

  # Extract YYYY MM DD HH MM SS from the filename.
  date_match = re.match(
      r'(\d\d\d\d)_(\d\d)_(\d\d)_(\d\d)_(\d\d)_(\d\d)\..*', flat_filename)
  if not date_match:
    raise ValueError('Could not extract date from %r.' % flat_filename)

  return flat_filename, datetime.datetime(*map(int, date_match.groups()))


