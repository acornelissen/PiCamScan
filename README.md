# PiCamScan

A simple little python webserver based on some example code from the picamera docs to interface with a Raspberry Pi and camera to scan film from a web interface, giving you a nice and compact scanning setup.

Does not rely on OpenCV, so can run on slower hardware.

It's good enough for web/mobile use, but I wouldn't make prints from the results.

## You'll need
* A Raspberry Pi (I used a Zero 2 W)
* A Raspberry Pi compatible camera (I used the HQ camera with 16mm lens)
* A tripod or copy stand
* A way to hold film flat (I'm using the holder and advancer from Valoi)
* A light source

## For the code, I have the following dependencies:
* PiCamera - https://picamera.readthedocs.io/en/release-1.13/
* PiDNG - https://github.com/schoolpost/PiDNG
* The chota micro CSS framework - https://jenil.github.io/chota/

## How to use it
Make sure your camera works, as per the instructions for your specific model. Tweak the camera config in `scanner.py` if necessary. 

SSH into yout Raspberry Pi and clone this repo. Run the webserver with `python3 scanner.py` and then navigate to `[raspi-ip-address]:8000` from any web browser on any machine on your local network.

You should see a live preview, which will assist you with alignment and focus. You can set a file prefix and number of frames to capture. Note than changing the number of frames mid-scan will reset the frame counter to 1.

Click "Scan" and wait! Once captured and converted to DNG, the file will automatically be downloaded. Advance to your next frame, click "Scan", and continue until you've scanned a roll.

The DNGs are ready for use and conversion in any application that supports it.

Stop the webserver on your Pi with Ctrl-C (this will shut down the camera and cleanup the output folder).