import serial
import time

# Create a serial connection
ser = serial.Serial('/dev/ttyUSB3', 115200, timeout=1)

# Wait for the modem to be ready
time.sleep(2)

# Clear input buffer
ser.reset_input_buffer()

# Send AT command to check modem connectivity
ser.write(b'AT\r\n')
response = ser.read_until(b'OK\r\n').decode('ASCII')

# Check if the modem responded correctly
if 'OK' not in response:
    print('Modem not responding correctly.')
    ser.close()
    exit()

# Set text mode
ser.write(b'AT+CMGF=1\r\n')
response = ser.read_until(b'OK\r\n').decode('ASCII')

# Check if the mode was set correctly
if 'OK' not in response:
    print('Failed to set text mode.')
    ser.close()
    exit()

# Specify the recipient number
recipient = '+370000000'

# Specify the message content
message = 'Test Text' \

# Send the AT+CMGS command to send the SMS
ser.write('AT+CMGS="{}"\r\n'.format(recipient).encode('ASCII'))
time.sleep(1)  # Wait for the modem to respond

# Send the message content
ser.write(message.encode('ASCII'))
time.sleep(0.5)  # Wait for the modem to process the message

# Send the Ctrl+Z (ASCII code 26) to indicate the end of the message
ser.write(bytes([26]))
time.sleep(1)  # Wait for the modem to send the SMS

# Read the response from the modem
response = ser.read_until(b'OK\r\n').decode('ASCII')

# Check if the SMS was sent successfully
if 'OK' in response:
    print('SMS sent successfully.')
else:
    print('Failed to send SMS.')

# Close the serial connection
ser.close()
