import serial
import numpy as np
import struct
import sys
from PIL import Image
from time import sleep

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
# while NanoVNA churns, create a gamma LUT to better match LCD
lut = np.array(np.rint(255*np.float_power(np.arange(256)/255,1.4)), dtype=np.uint32)

# need to prune 9 leading bytes b'capture\r\n'
prune = 9
# nanoVNA has 320 x 240 RGB565 screen buffer = 7680 half-words
blen = prune + 320 * 240 * 2
buffer = ser.read(blen)

#print(len(buffer))
#print(buffer[0:prune])
#print(buffer.find(b"\n"))
# Recalculate prune and blen based on newline
#prune = 1 + buffer.find(b"\n")
#blen = prune + 320 * 240 * 2

# unlikely to grab entire screen buffer in one read()
while (blen > (len(buffer))):
    sleep(0.1)
    buffer += ser.read(blen)

# expand 16-bit RGB half-words from buffer to np.array of 32-bit words
# prune leading and trailing buffer:  buffer[prune:blen]
# ">" for big-endian, "H" for 16-bit half-words
xBGR = np.array(struct.unpack(">76800H", buffer[prune:blen]), dtype=np.uint32)

# convert nanoVNA pixel format 565(RGB) to 8888(RGBX)
# X is unused and ignored; numpy cannot directly support 24-bit color words
# could in theory use stride_tricks https://stackoverflow.com/a/34128171
xBGR = (lut[(xBGR & 0x001F)<<3]<<16) + (lut[(xBGR & 0x07E0)>>3]<<8) + lut[(xBGR & 0xF800)>>8]

# https://pillow.readthedocs.io/en/3.1.x/reference/Image.html
# Image.frombuffer('RGBX', ...) expects xBGR byte sequence, ignoring most significant byte
Image.frombuffer('RGBX', (320, 240), xBGR, 'raw', 'RGBX', 0, 1).save(str(sys.argv[1])+'.png')
