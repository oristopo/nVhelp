# send a single nanoVNA command and delete that command string from return
import sys
from serial import Serial
import re
from time import sleep

#print('Number of arguments:', len(sys.argv), 'arguments.')
#print('Argument List:', str(sys.argv))

if 1 < len(sys.argv) :
    port = 'COM3'
    try:
        ser = Serial(port, 9600, timeout=0)
        try:
# sync with nanoVNA, already in progress
            data = "a"
            while data != "":
                data = ser.readline().decode('ascii')
# send any valid nanoVNA command
# https://groups.io/g/nanovna-users/wiki/shellcommands
            command = str(sys.argv[1])+"\r"
            ser.write(command.encode('ascii'))
            sleep(0.1)
            result = ""
# collect results until nanoVNA returns its shell prompt
            while "ch>" not in data:
# strip "\r"
                result += data.replace("\r", "")
                data = ser.readline().decode('ascii')

# To delete echoed command: search for first newline
            d = re.search("\n", result)
            if d is None :
                sys.stderr.write("no lines returned from nanoVNA")
                print('['+result+']')
            else :
                print(result[1+d.start():], end = '')

        except ser.SerialException:
            sys.stderr.write('nanoVNA could not be read')

    except (OSError, serial.SerialException):
        sys.stderr.write(port+' not found')
else :
    sys.stderr.write(str(sys.argv[0])+": nanoVNA command argument expected")
