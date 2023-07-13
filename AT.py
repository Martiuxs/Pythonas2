import serial
import time

ser = serial.Serial('/dev/ttyUSB3', 115200, timeout=1)

command = "ATI\r\n"
print("Sending command:", command)
ser.write(bytes(command, encoding='utf-8'))

time.sleep(0.1)

response = ser.read_all().decode('utf-8')
# Process the response
print("Received response:", response)

ser.close()
