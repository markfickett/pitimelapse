import argparse
import logging
import os


SKIP_PROJECTS = (
    'var',
    'archive',
)


def ApplyPerProject(args, fn, *passthrough_args, **kwargs):
  src_dir_path, dst_dir_path = _Expand(args.src), _Expand(args.dst)
  processed = []
  for project_dir in os.listdir(src_dir_path):
    if project_dir in SKIP_PROJECTS:
      continue
    if args.project and project_dir not in args.project:
      continue
    processed.append(project_dir)
    fn(
        os.path.join(src_dir_path, project_dir),
        os.path.join(dst_dir_path, project_dir),
        *passthrough_args,
        **kwargs)
  logging.info(
      'Processed %d projects in %r: %s.',
      len(processed), src_dir_path, ' '.join(processed))


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
  parser.add_argument(
      '-p', '--project', action='append',
      help='Process only these projects.')
  return parser


def ConfigureLogging():
  logging.basicConfig(
      format='%(levelname)s %(asctime)s %(filename)s:%(lineno)s: %(message)s',
      level=logging.INFO)
