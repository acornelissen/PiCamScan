# PiCamScan: A web interface to scan film to DNGs using a Raspberry Pi and camera
#
# Based on the Web streaming example:
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import os
import logging
import socketserver

from urllib.parse import urlparse
from threading import Condition
from http import server

import picamera
from pidng.core import RPICAM2DNG

# Get index template
web_index = ''
with open('index.html', encoding = 'utf8') as f:
    web_index = f.read()

# Set up camera object - these settings are specific to the Pi HQ camera, update or tweak them as needed for your setup
camera = picamera.PiCamera()
camera.resolution = (1024, 768)
camera.sensor_mode = 3
camera.framerate = 24

# Streaming output object for MJPEG camera stream / live preview
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

# Webserver / route handling
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = web_index.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path.startswith('/capture'):

            # Check if a filename prefix was supplied and use it, or default to "scan"
            query = urlparse(self.path).query
            filename = 'scan'

            if query:
                query_components = dict(qc.split("=") for qc in query.split("&"))
                filename = query_components["filename"]

            content = filename.encode('utf-8')

            # Capture RAW bayer array
            filename_proc = "output/" + filename + ".jpg"
            camera.capture(filename_proc , format='jpeg', bayer=True)

            # Convert just captured RAW bayer array to DNG
            d = RPICAM2DNG()
            d.convert(filename_proc)

            # Remove original JPG with RAW bayer array
            os.remove(filename_proc)

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()

            # Stream MJPEG from camera
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path.endswith('.css') or self.path.endswith('.js') or self.path.endswith('.dng'):

            # Serve static files with relevant read open methods and content type headers 
            f = open(os.getcwd() + self.path, encoding = 'utf8')
            if self.path.endswith('.dng'):
                f = open(os.getcwd() + self.path, 'rb')

            self.send_response(200)

            if self.path.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif self.path.endswith('.js'):
                self.send_header('Content-type', 'text/javascript')
            elif self.path.endswith('.dng'):
                self.send_header('Content-type', 'image/DNG')
                self.send_header('Content-Disposition', 'attachment')

            self.end_headers()

            if self.path.endswith('.dng'):
                self.wfile.write(f.read())
            else:
                self.wfile.write(f.read().encode('utf-8'))

            f.close()
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# Create streaming object and start the preview
output = StreamingOutput()
camera.start_recording(output, format='mjpeg')

# Start the webserver
try:
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    # Stop the preview / camera
    camera.stop_recording()

    # Cleanup output folder
    folder = os.getcwd() + '/output'

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.unlink(file_path)
