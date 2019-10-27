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
# create a gamma LUT while nanoVNA churns
lut = np.array(np.rint(255*np.float_power(np.arange(256)/255,1/2.4)), dtype=np.uint32)

# need to prune leading bytes
prune = 9
# nanoVNA has 320 x 240 RGB565 screen buffer
blen = prune + 320 * 240 * 2
b = ser.read(blen)
#print(len(b))
#print(b[0:prune])
#print(b.find(b"\n"))
#recalculate prune and blen based on newline
#prune = 1 + b.find(b"\n")
#blen = prune + 320 * 240 * 2
# unlikely to grab entire screen buffer in one read()
while (blen > (len(b))):
    sleep(0.1)
    b += ser.read(blen)

# prune leading and trailing
# ">" for big-endian 16-bit
x = struct.unpack("<76800H", b[prune:blen])

# unpack uint16 to uint32
arr = np.array(x, dtype=np.uint32)
# convert pixel format 565(RGB) to 8888(RGBA)
# while A (alpha) is unused, numpy does not directly support 24-bit color values
# could in theory use stride_tricks https://stackoverflow.com/a/34128171
arr = 0xFF000000 + (lut[(arr & 0xF800) >> 8]<<16) + (lut[(arr & 0x07E0) >> 3]<<8) + lut[(arr & 0x001F) << 3]

# wants alpha as most significant byte
img = Image.frombuffer('RGBA', (320, 240), arr, 'raw', 'RGBA', 0, 1)
img.save(str(sys.argv[1])+'.png')
