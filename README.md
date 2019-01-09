# Time Lapse Processing Scripts for Raspberry Pi

## Overview

On a Raspberry Pi (`capture_and_upload.sh`)

*   Capture images at regular intervals, with timestamped names and into year/month/day directories.
*   Use `rsync` to copy images to a remote server.
*   Monitor free space and trim old images from local storage.

On a server storing the images (`copy_latest.py` and `make_videos.py`)

*   Copy the latest image from each Pi/project to a web server directory.
*   Add filename / copyright overlays to images, create proxy resolution images.
*   Create time lapse videos for each project, either using all images or the latest 24 hours of images.

## Hardware

I set up a Pi B+ with a 3D-printed camera case, syncing images over WiFi.

*   Raspberry Pi with camera connector (such as [the B+](http://adafru.it/1914), $30)
*   Raspberry Pi camera ([$20](http://adafru.it/1367))
*   [USB WiFi module with antenna for $20](http://adafru.it/1030) with significantly more reliable connection than small/no antenna options; or [bare-board USB WiFi dongle for $4](https://www.amazon.com/dp/B0113VBNKA)
*   Reliable 5V USB power. Many USB wall warts supply less than 5V, and many USB cables have significant voltage drop. If you see occasional brownouts (which can manifest as SD card corruption, garbage in `/var/log/messages`, freezes, ...), check your power supply. Some references:
    *   [Diagnosing power supply problems](http://elinux.org/RPi_Hardware#Power_supply_problems)
    *   [Adafruit's Pi B+ power supply article](https://learn.adafruit.com/introducing-the-raspberry-pi-model-b-plus-plus-differences-vs-model-b/power-supply)
*   Camera mount, one of:
    *   [Suction cup clamp mount for $8](https://smile.amazon.com/IPOW-Universal-Windshield-Dashboard-Suction/dp/B013Y4S2RQ). Easy to adjust the angle, reliable in sunlight.
    *   [3D printed Pi/camera suction cup mount](http://www.thingiverse.com/thing:1592053) ([modeled in TinkerCad](https://tinkercad.com/things/8DpHAWdNvYx)). Deformed gradually in sunlight. Along with small suction cups from the hardware store, a convenient way to hold both the Pi and its camera.
    *   Painter's tape. If mounting the camera flush against the window points it the right way, this is easiest.

At almost $100, this setup is actually somewhat competitive with commercial WiFi webcams, especially considering 5MP camera resolution, customizable software, and reusable parts.

## Headless image preview

There's [a Pi forum thread](https://www.raspberrypi.org/forums/viewtopic.php?t=119960&p=812018) outlining how to view a video stream from a Pi over a network using VLC. Briefly:

```
sudo apt-get update && sudo apt-get install vlc
raspivid -o - -t 0 -n -w 640 -h 480 -fps 25 | cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8081}' :demux=h264
```

Then view `http://your-raspberry-pi:8081` in VLC (`mplayer` also works).

### Aligning cameras

To align multiple cameras to the same point (ex: capturing a stereo pair), you can add crude crosshairs in VLC. Following [VLC's help doc on adding overlays](https://www.vlchelp.com/add-logo-watermarks-over-videos-vlc/), use `Window > Video Effects...` then in the `Misc` tab, `Add text`.

### SSH tunnel

If you can't `ssh` in to your Pi, but can log in and set up a tunnel:

*   Log into the Pi.
*   Start the VLC stream.
*   `pi@pi $ ssh -R 8082:localhost:8081 timelapse@timelapse.com -Nv` forwards connections from `timelapse.com:8082` to the Pi's port `8081`. But this is a reverse tunnel so `timelapse.com:8082` is only available locally (I can't use `-g`).
*   `me@laptop $ ssh -L 8083:localhost:8082 me@timelapse.com -Nv` forwards connections to `localhost:8083` on my laptop to `timelapse.com:8082`, matching up with the other tunnel.
*   On my laptop, open VLC and view `http://localhost:8083`.

## WiFi configuration

For an open network named `MIT GUEST`, edit `/etc/wpa_supplicant/wpa_supplicant.conf` and add:

```
network = {
  ssid="MIT GUEST"
  key_mgmt=NONE
}
```

More in the [Pi WiFi docs](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md).

## Reimage the Pi

[OS Installation Instructions](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)

```
diskutil unmountDisk /dev/disk2
sudo dd bs=1m if=/path/to/.../*raspbian*.img of=/dev/rdisk2 conv=sync
^T  # for status
```

After boot, run `sudo raspi-config`.

## Connecting to a Pi

If simply `ssh`ing into the Pi isn't available:

### Log in over Serial

See [RPi Serial Connection](http://elinux.org/RPi_Serial_Connection), also a [Pi Zero walkthrough](http://hackers.gallery/850/misc/raspberry-pi-zero-setting-up-wifi-over-the-serial-console).

Breifly: `screen /dev/tty.usbserial-A50285BI 115200`. From the corner pin (opposite USB ports), the pins are 5V, 5V, Ground, Tx, Rx. Connect Ground/Tx/Rx to a 3.3v USB serial connector.

### Share wired network from a Mac

*   Connect Mac to Pi using ethernet cable.
*   System Preferences... > Sharing > Internet Sharing
*   Run `arp -i bridge100 -a` to find connected clients' IP addresses. Note that the bridge network won't be created unless the host Mac has a WiFi connection (not just having WiFi on).
*   `ssh 192.168.2.3` or whatever your Pi's address is.

## Related

[RPi timelapse using USB webcam](https://github.com/alvarop/timelapse)
