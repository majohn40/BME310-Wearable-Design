import serial

ser = serial.Serial(
    port='COM4',\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

print("connected to: " + ser.portstr)
count=1

while True:
	while ser.in_waiting:
		sensor_reading = ser.readline()
		print(sensor_reading.decode('utf-8'))

ser.close()