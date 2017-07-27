import os
import re


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
