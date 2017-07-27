import argparse
import logging
import os


SKIP_PROJECTS = (
    'var',
    'archive',
)


def ApplyPerProject(src_raw, dst_raw, fn, *args, **kwargs):
  src_dir_path, dst_dir_path = _Expand(src_raw), _Expand(dst_raw)
  for project_dir in os.listdir(src_dir_path):
    if project_dir in SKIP_PROJECTS:
      continue
    fn(
        os.path.join(src_dir_path, project_dir),
        os.path.join(dst_dir_path, project_dir),
        *args,
        **kwargs)


def _Expand(raw_path):
  return os.path.abspath(os.path.expanduser(raw_path))


def GetSrcDstParser():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      'src',
      help='Project directory, containing either YYYY dirs or flat files.')
  parser.add_argument(
      'dst',
      help='Output directory in which to create project subdir and latest.jpg.')
  return parser


def ConfigureLogging():
  logging.basicConfig(
      format='%(levelname)s %(asctime)s %(filename)s:%(lineno)s: %(message)s',
      level=logging.INFO)
