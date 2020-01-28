from serial import Serial
import numpy as np
import struct
import sys
from PIL import Image
from time import sleep

# https://github.com/ttrftech/NanoVNA/blob/master/python/nanovna.py

def open():
    port = 'COM3'
    try:
        ser = Serial(port, 9600, timeout=0)
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
# while NanoVNA churns, create a gamma LUT to better match LCD
lut = np.array(np.rint(255*np.float_power(np.arange(256)/255,1.4)), dtype=np.uint32)

# need to prune 9 leading bytes b'capture\r\n'
prune = 9
# nanoVNA has 320 x 240 RGB565 screen buffer = 76800 half-words
# nanoVNA-H4 has 480 x 320 RGB565 screen buffer = 153600 half-words
blen = prune + 480 * 320 * 2
sleep(0.1)
buffer = ser.read(blen)

# unlikely to grab entire screen buffer in one read()
# for some unknown reason, first attempts using Windows 10 Store Python 3.7.3
# failed to return enough bytes after looping many times..
# It started working after a half dozen or so attempts..??
#print(blen)
sofar = 0
#while (blen > (len(buffer))):
while (sofar < (len(buffer))):
    sofar = len(buffer)
#   print(sofar)
    sleep(0.1)
    buffer += ser.read(blen)

# expand 16-bit RGB half-words from buffer to np.array of 32-bit words
# prune leading and trailing buffer:  buffer[prune:blen]
# ">" for big-endian, "H" for 16-bit half-words
if (sofar > 200000):
    aBGR = np.array(struct.unpack(">153600H", buffer[prune:blen]), dtype=np.uint32)
else:
    blen = prune + 320 * 240 * 2
    aBGR = np.array(struct.unpack(">76800H", buffer[prune:blen]), dtype=np.uint32)

# convert nanoVNA pixel format 565(RGB) to 8888(RGBA)
# A is unused and ignored; numpy cannot directly support 24-bit color words
# could in theory use stride_tricks https://stackoverflow.com/a/34128171
aBGR = 0xFF000000 + (lut[(aBGR & 0x001F)<<3]<<16) + (lut[(aBGR & 0x07E0)>>3]<<8) + lut[(aBGR & 0xF800)>>8]

# https://pillow.readthedocs.io/en/3.1.x/reference/Image.html
# Image.frombuffer('RGBA', ...) expects aBGR byte sequence, ignoring most significant byte
if (sofar > 200000):
    Image.frombuffer('RGBA', (480, 320), aBGR, 'raw', 'RGBA', 0, 1).save(str(sys.argv[1])+'.png')
else:
    Image.frombuffer('RGBA', (320, 240), aBGR, 'raw', 'RGBA', 0, 1).save(str(sys.argv[1])+'.png')
