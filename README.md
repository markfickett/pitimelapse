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

## WiFi configuration

For an open network named `MIT GUEST`, edit `/etc/wpa_supplicant/wap_supplicant.conf` and add:

```
network = {
  ssid="MIT GUEST"
  key_mgmt=NONE
}
```

More in the [Pi WiFi docs](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md).

## SSH / remote video preview

My time lapse cameras are on a somewhat flaky public WiFi network. They don't have public IP addresses, they may get new local IPs, and anyway clients are on private VLANs so I can't see the Pis even when I'm on the same network.

### SSH

How to get occasional SSH access?

Suppose I have a server `timelapse.com`, with SSH access from the Pis and from my laptop.

I add this to the Pi's `crontab`:

```
0 * * * * flock -n /tmp/sshreverse.lock ssh -R 2220:localhost:22 timelapse@timelapse.com -Nv
```

Now every hour, it tries to reopen a reverse tunnel. Connections to `timelapse.com:2220` are forwarded to the Pi's port `22` (standard SSH port). Using `flock -n` means the cron job will only attempt to connect if the previous SSH command has exited. I [set up SSH keys](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2) so the Pi doesn't need a password to log in to `timelapse.com`.

Reverse tunnels (even to non-privileged ports) are only accessible locally, so first I SSH into `timelapse.com`, and then I can SSH into the Pi:

```
me@timelapse.com $ ssh -p 2220 pi@localhost
```

### Video Preview

How to view a video feed from the Pi?

*   SSH into the Pi (using the reverse tunnel if necessary).
*   Start the VLC stream.
*   `pi@pi $ ssh -R 8082:localhost:8081 timelapse@timelapse.com -Nv` forwards connections from `timelapse.com:8082` to the Pi's port `8081`. But this is a reverse tunnel so `timelapse.com:8082` is only available locally.
*   `me@laptop $ ssh -L 8083:localhost:8082 me@timelapse.com -Nv` forwards connections to `localhost:8083` on my laptop to `timelapse.com:8082`, matching up with the other tunnel.
*   On my laptop, open VLC and view `http://localhost:8083`.
