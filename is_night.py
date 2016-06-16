#!/usr/bin/env python
# Exits with status 0 if it is night, otherwise 1.
# Usage:
#     if ./is_night.py 'Boston'; then echo 'night'; else echo 'day'; fi
# or
#     ./is_night 42.368957 -71.123198
import sys
import ephem # sudo pip install ephem

if len(sys.argv) == 2:
  observer = ephem.city(sys.argv[1])
else:
  observer = ephem.Observer()
  observer.lat = sys.argv[1]
  observer.lon = sys.argv[2]

sun = ephem.Sun()
sun.compute(observer)
sys.exit(1 if sun.alt > 0 else 0)
