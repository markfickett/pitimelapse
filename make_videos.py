#!/usr/bin/env python
"""
Makes a time lapse video from stills.
"""

import logging
import os
import re
import shutil
import subprocess

from main_util import ApplyPerProject
from main_util import ConfigureLogging
from main_util import GetSrcDstParser
from project import GetProjectLatest
from project import IterProject


PROXY_SIZE = 1280
PROXY_DIR = 'var'  # created as a sibling of the project(s)
WATERMARK = 'markfickett.com'
FRAMES_CAPTURED_PER_HOUR = 6.0  # Assume all projects take frames every 10m.


def MakeVideo(project_src_dir_path, project_dst_dir_path, fps, realtime_hours):
  proxy_project_path = _UpdateProxies(project_src_dir_path)
  out_video_path = os.path.join(
      project_dst_dir_path,
      '%s.mp4' % ('' if realtime_hours is None else '%dh' % realtime_hours))
  if not _LatestImageNewer(project_src_dir_path, out_video_path):
    return
  logging.info(
      'Generating video for %s at %s.', proxy_project_path, out_video_path)

  # When played back at `fps`, how much video time do we need in order to
  # cover `realtime_hours`? This determines the "slice" argument to ffmpeg.
  slice_args = []
  if realtime_hours:
    slice_args.append('-sseof')
    # TODO Determine real elapsed time from frame timestamps, and avoid
    # overrunning if we have too few available frames.
    num_frames = realtime_hours * FRAMES_CAPTURED_PER_HOUR
    output_seconds = num_frames / fps
    slice_args.append('-%.2f' % output_seconds)

  subprocess.check_call([
    'ffmpeg',
    '-r', str(fps),
    '-y',
  ] + slice_args + [
    '-pattern_type', 'glob',
    '-i', '%s%s*.jpg' % (proxy_project_path, os.path.sep),
    '-c:v', 'libx264',
    out_video_path,
  ])


def _LatestImageNewer(project_src_dir_path, target_file_path):
  latest_filename = GetProjectLatest(project_src_dir_path)
  if not latest_filename:
    return False
  if not os.path.isfile(target_file_path):
    return True
  return os.path.getmtime(latest_filename) > os.path.getmtime(target_file_path)


def _GetFlatFileName(flat_or_hierarchical_path):
  _, local_filename = os.path.split(flat_or_hierarchical_path)
  if re.match(r'^\d\d\d\d_.*$', local_filename):
    return local_filename
  else:
    return '_'.join(flat_or_hierarchical_path.split(os.path.sep)[-4:])


def _UpdateProxies(project_src_dir_path):
  src_dir_path, project_name = os.path.split(project_src_dir_path)
  proxy_project_path = os.path.join(
      src_dir_path, PROXY_DIR, '%s_%d' % (project_name, PROXY_SIZE))
  if not os.path.isdir(proxy_project_path):
    shutil.makedirs(proxy_project_path)
  for filename in IterProject(project_src_dir_path, reverse=True):
    local_flat_filename = _GetFlatFileName(filename)
    proxy_path = os.path.join(proxy_project_path, local_flat_filename)
    if os.path.isfile(proxy_path):
      continue  # TODO Default to trust that there are no gaps?
    # Run `sudo apt-get install imagemagick` for `convert`.
    subprocess.check_call([
        'convert',
        '-resize', '%dx%d' % (PROXY_SIZE, PROXY_SIZE),
        '-background', '#0008', '-fill', 'white',
        '-gravity', 'west', '-size', '%dx20' % PROXY_SIZE,
        'caption:%s %s' % (WATERMARK, local_flat_filename),
        filename,
        '+swap',
        '-gravity', 'south',
        '-composite',
        proxy_path,
    ])
    logging.info('Proxied %s at %s.', filename, proxy_path)
  return proxy_project_path


if __name__ == '__main__':
  ConfigureLogging()
  parser = GetSrcDstParser()
  parser.add_argument('--fps', type=int, default=30)
  parser.add_argument(
      '--realtime_hours', type=int,
      help='Real-world hours to cover in the time lapse (at most).')
  args = parser.parse_args()
  ApplyPerProject(args.src, args.dst, MakeVideo, args.fps, args.realtime_hours)
