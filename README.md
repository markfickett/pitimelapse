# Time Lapse Processing Scripts for Raspberry Pi

## Overview

On a Raspberry Pi (`capture_and_upload.sh`)

*   Capture images at regular intervals, with timestamped names and into year/month/day directories.
*   Use `rsync` to copy images to a remote server.
*   Monitor free space and trim old images from local storage.

On a server storing the images (`copy_latest.sh` and `make_videos.sh`)

*   Copy the latest image from each Pi/project to a web server directory.
*   Add filename / copyright overlays to images, create proxy resolution images.
*   Create time lapse videos for each project, either using all images or the latest 24 hours of images.

## Hardware

I set up a Pi B+ on a 3D-printed suction cup window mount, syncing images over WiFi.

*   Raspberry Pi with camera connector (such as [the B+](http://adafru.it/1914), $30)
*   Raspberry Pi camera ([$20](http://adafru.it/1367))
*   [USB WiFi module with antenna for $20](http://adafru.it/1030) with significantly more reliable connection than small/no antenna options; or [bare-board USB WiFi dongle for $4](https://www.amazon.com/dp/B0113VBNKA)
*   Suction cups from the local hardware store
*   [3D printed Pi/camera suction cup mount](http://www.thingiverse.com/thing:1592053), [modeled in TinkerCad](https://tinkercad.com/things/8DpHAWdNvYx); Thingiverse will print it for $20 shipped.

At almost $100, this setup is actually somewhat competitive with commercial WiFi webcams, especially considering 5MP camera resolution, customizable software, and reusable parts.

## Headless image preview

There's [a Pi forum thread](https://www.raspberrypi.org/forums/viewtopic.php?t=119960&p=812018) outlining how to view a video stream from a Pi over a network using VLC. Briefly:

```
sudo apt-get update && sudo apt-get install vlc
raspivid -o - -t 0 -n -w 640 -h 480 -fps 25 | cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8081}' :demux=h264
```

Then view `http://localhost:8081` in VLC (`mplayer` also works).

## Aligning cameras

To align multiple cameras to the same point (ex: capturing a stereo pair), you can add crude crosshair in VLC. Following [VLC's help doc on adding overlays](https://www.vlchelp.com/add-logo-watermarks-over-videos-vlc/), use `Window > Video Effects...` then in the `Misc` tab, `Add text`.