import serial
import numpy as np
import struct
import sys
from PIL import Image

# https://github.com/ttrftech/NanoVNA/blob/master/python/nanovna.py

def open():
    port = 'COM3'
    try:
        ser = serial.Serial(port, 9600, timeout=0)
        try:
# sync with nanoVNA, already in progress
            data = "a"
            while data != "":
                data = ser.readline().decode('ascii')
            return ser

        except ser.SerialException:
            sys.stderr.write('nanoVNA could not be read')
            exit(3)

    except (OSError, serial.SerialException):
        sys.stderr.write(port+' not found')
        exit(2)

#
# if there were main(), then it would be here
#

if 2 > len(sys.argv) : 
    sys.stderr.write(str(sys.argv[0])+": PNG filename (without .png) expected") 
    exit(1)

cmd = "capture\r"
ser = open()
ser.write(cmd.encode())

# will need to prune leading bytes
prune = 9
# nanoVNA has 320 x 240 RGB565 screen buffer
blen = prune + 320 * 240 * 2
b = ser.read(blen)
# unlikely to grab entire screen buffer in one read()
while (blen > (len(b))):
    b += ser.read(blen)

# prune leading and trailing
b = b[prune:blen]

# ">" for big-endian 16-bit
x = struct.unpack("<76800H", b)

# unpack uint16 to uint32
arr = np.array(x, dtype=np.uint32)
# convert pixel format 565(RGB) to 8888(ARGB)
# while A (alpha) is unused, numpy does not directly support 24-bit color values
# could in theory use stride_tricks https://stackoverflow.com/a/34128171
arr = 0xFF000000 + ((arr & 0xF800) << 8) + ((arr & 0x07E0) << 5) + ((arr & 0x001F) << 3)

img = Image.frombuffer('RGBA', (320, 240), arr, 'raw', 'RGBA', 0, 1)
img.save(str(sys.argv[1])+'.png')
