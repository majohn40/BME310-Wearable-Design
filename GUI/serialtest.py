import serial
import time

ser = serial.Serial(
    port='COM4',\
    baudrate=115200,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
        timeout=0)

print("connected to: " + ser.portstr)
count=1

ser.flushInput()
ser.flushOutput()

while True:
	if ser.in_waiting:
		sensor_packet = ser.readline().decode('utf-8')
		sensors = sensor_packet.split("\t")
		if len(sensors) == 7:
			print("Accelerometer: "+sensors[0])
		print(sensor_packet)
		time.sleep(0.01)

ser.close()