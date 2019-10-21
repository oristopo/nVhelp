import sys
import serial
from time import sleep

#print('Number of arguments:', len(sys.argv), 'arguments.')
#print('Argument List:', str(sys.argv))

if 1 < len(sys.argv) :
    port = 'COM3'
    try:
        ser = serial.Serial(port, 9600, timeout=0)
        try:
# sync with nanoVNA, already in progress
            data = "a"
            while data != "":
                data = ser.readline().decode('ascii')
# send any valid nanoVNA command
            command = str(sys.argv[1])+"\r"
# https://groups.io/g/nanovna-users/files/NanoVNA%20Console%20Commands%20Oct-16-19.pdf
            ser.write(command.encode('ascii'))
# echo'ed command becomes a comment in gnuplot-able results
            result = "# "
            sleep(0.1)
# collect results until nanoVNA returns its shell prompt
            while "ch>" not in data:
                result += data
                data = ser.readline().decode('ascii')

            print(result)

        except ser.SerialException:
            sys.stderr.write('Data could not be read')

    except (OSError, serial.SerialException):
        sys.stderr.write(port+' not found')
else :
    sys.stderr.write(str(sys.argv[0])+": nanoVNA command argument expected")
