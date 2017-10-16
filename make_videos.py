#!/usr/bin/env python
"""
Makes a time lapse video from stills.
"""

import datetime
import logging
import os
import re
import subprocess
import tempfile

from main_util import ApplyPerProject
from main_util import ConfigureLogging
from main_util import GetSrcDstParser
from project import GetFlatFileNameAndTime
from project import GetProjectLatest
from project import IterProject


PROXY_SIZE = 1280
PROXY_DIR = 'var'  # created as a sibling of the project(s)
WATERMARK = 'markfickett.com'


def MakeVideo(
    project_src_dir_path,
    project_dst_dir_path,
    fps,
    pattern,
    realtime_hours=None,
    output_filename=None,
    force=False):
  if output_filename is None:
    out_video_path = os.path.join(
        project_dst_dir_path,
        '%s%dfps.mp4' % (
            '' if realtime_hours is None else '%dh_' % realtime_hours,
            fps))
  else:
    out_video_path = os.path.join(project_dst_dir_path, output_filename)

  if not _LatestImageNewer(project_src_dir_path, out_video_path):
    logging.info(
        'Latest file for %r not newer than %r. %s',
        project_src_dir_path,
        out_video_path,
        'Overwriting.' if force else 'Skipping.')
    if not force:
      return

  proxy_project_path = _GetProxyProjectPath(project_src_dir_path)
  logging.info(
      'Generating video for %s at %s.', proxy_project_path, out_video_path)

  oldest_frame_time = None
  if realtime_hours:
    oldest_frame_time = datetime.datetime.utcnow() - datetime.timedelta(
        hours=realtime_hours)

  with tempfile.TemporaryFile() as frame_list_file:
    for frame_path in reversed(list(_IterUpdatedProxies(
        project_src_dir_path, proxy_project_path, oldest_frame_time, pattern))):
      frame_list_file.write(
          "file '%s/%s'\nduration %d\n" %
          (proxy_project_path, frame_path, 1000 / fps))

    # https://trac.ffmpeg.org/wiki/Slideshow
    # Both output frame rate here and duration above in the frame list to
    # concatenation seem to be required.
    ffmpeg_cmd = [
      'ffmpeg',
      '-r', str(fps),
      '-y',  # Overwrite output files without asking.
      '-f', 'concat',
      '-i', '-',  # Frame list file read from stdin.
      '-vsync', 'vfr', '-pix_fmt', 'yuv420p',
      out_video_path,
    ]
    logging.info(' '.join(map(repr, ffmpeg_cmd)))
    frame_list_file.seek(0)
    subprocess.check_call(ffmpeg_cmd, stdin=frame_list_file)


def _LatestImageNewer(project_src_dir_path, target_file_path):
  latest_filename = GetProjectLatest(project_src_dir_path)
  if not latest_filename:
    logging.info('No latest file in %r.', project_src_dir_path)
    return False
  if not os.path.isfile(target_file_path):
    return True
  return os.path.getmtime(latest_filename) > os.path.getmtime(target_file_path)


def _GetProxyProjectPath(project_src_dir_path):
  src_dir_path, project_name = os.path.split(project_src_dir_path)
  proxy_project_path = os.path.join(
      src_dir_path, PROXY_DIR, '%s_%d' % (project_name, PROXY_SIZE))
  if not os.path.isdir(proxy_project_path):
    os.makedirs(proxy_project_path)
  return proxy_project_path


def _IterUpdatedProxies(
    project_src_dir_path, proxy_project_path, oldest_frame_time, pattern):
  for filename in IterProject(project_src_dir_path, reverse=True):
    local_flat_filename, frame_time = GetFlatFileNameAndTime(filename)
    if (oldest_frame_time is not None) and (frame_time < oldest_frame_time):
      logging.info(
          '%s (%s) older than %s, done iterating.',
          filename, frame_time, oldest_frame_time)
      return
    if not re.match(pattern, local_flat_filename):
      continue
    proxy_path = os.path.join(proxy_project_path, local_flat_filename)
    if not os.path.isfile(proxy_path):
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
    yield local_flat_filename


if __name__ == '__main__':
  ConfigureLogging()
  parser = GetSrcDstParser()
  parser.add_argument('--fps', type=int, default=15)
  parser.add_argument(
      '--realtime_hours', type=int,
      help='Real-world hours to cover in the time lapse (at most).')
  parser.add_argument(
      '--pattern', default=r'.*',
      help='Use this regular expression to select frames for the video.'
           + ' The pattern is matched against proxy image local filenames.')
  parser.add_argument(
      '-o', '--out',
      help='Local filename (ex: video.mp4) for output video file. By default,'
           + ' a filename is generated from fps and duration.')
  parser.add_argument(
      '-f', '--force', action='store_true',
      help='Always regenerate the video, even if no new frames are detected.')
  args = parser.parse_args()
  ApplyPerProject(
      args,
      MakeVideo,
      args.fps,
      args.pattern,
      realtime_hours=args.realtime_hours,
      output_filename=args.out,
      force=args.force)
