import sys
import serial
from time import sleep

#print('Number of arguments:', len(sys.argv), 'arguments.')
#print('Argument List:', str(sys.argv))

# send any valid nanoVNA command
# https://groups.io/g/nanovna-users/files/NanoVNA%20Console%20Commands%20Oct-16-19.pdf
def serIO ( command ):
# sync with nanoVNA, already in progress
    data = "a"
    while data != "":
        data = ser.readline().decode('ascii')
# echo'ed command becomes a comment in gnuplot-able results
    ser.write(command.encode('ascii'))
    result = "# "
    sleep(0.1)
# collect results until nanoVNA returns its shell prompt
    while "ch>" not in data:
# strip "\r"
        result += data.replace("\r", "") 
        data = ser.readline().decode('ascii')
    return result

# the buck starts here
if 1 < len(sys.argv) :
    port = 'COM3'
    try:
        ser = serial.Serial(port, 9600, timeout=0)
        try:
            serIO("pause\r")
            for i in range(1, len(sys.argv)):
                print(serIO(str(sys.argv[i])+"\r"), end = '')
            serIO("resume\r")

        except ser.SerialException:
            sys.stderr.write('Data could not be read')

    except (OSError, serial.SerialException):
        sys.stderr.write(port+' not found')
else :
    sys.stderr.write(str(sys.argv[0])+": nanoVNA command argument expected")
