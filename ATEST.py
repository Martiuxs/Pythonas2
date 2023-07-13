# import serial
# import configparser

# # Read the configuration file
# config = configparser.ConfigParser()
# config.read('commands.ini')

# # Establish a serial connection with the TRM240 router
# ser = serial.Serial('/dev/ttyUSB3', 115200, timeout=1)

# # Iterate over the sections in the configuration file
# for section in config.sections():
#     # Retrieve the command and expected result from each section
#     command = section
#     expected_result = config[section]['ExpectedResult']

#     # Send the AT command
#     ser.write(f'{command}\r\n'.encode('ASCII'))

#     # Read the response
#     response = ser.read_until(b'OK\r\n').decode('ASCII').strip()

#     # Compare the response with the expected result
#     if response.find('OK') != -1:
#         print(f"Command '{command}' passed.")
#     else:
#         print(f"Command '{command}' failed. Expected: {'OK'}, Received: {response}")

# # Close the serial connection
# ser.close()
#######################################################################################################
import serial
import configparser
import csv
from datetime import datetime
from colorama import Fore, Style
import json

def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            return config
    except json.JSONDecodeError:
     raise ValueError(f"Error: Invalid JSON format in {file_path}")
data = load_config('Commands.json')

device = {}

productName = "TRM240"

for device in data['devices']:
    if(device['name'] == productName):
        device = device
        break




config = configparser.ConfigParser()
config.read('commands.ini')

ser = serial.Serial('/dev/ttyUSB3', 115200, timeout=1)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

file_name = f"{'TRM240'}_{timestamp}.csv"

# Counters for passed, failed, and total commands
passed_commands = 0
failed_commands = 0
total_commands = len(config.sections())

# Open the CSV file in write mode
with open(file_name, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(['Command', 'Expected Result', 'Received Result', 'Status'])

    # Iterate over the AT commands
    for section in config.sections():
        # Retrieve the command and expected result from each section
        command = section
        expected_result = config[section]['ExpectedResult']

        # Send the AT command
        ser.write(f'{command}\r\n'.encode('ASCII'))

        # Read the response
        response = ser.read_until(b'OK\r\n').decode('ASCII').strip()

        if response.find('OK') != -1:
            status = 'Passed'
            passed_commands += 1
        else:
            status = 'Failed'
            failed_commands += 1
       # Write the row to the CSV file
        writer.writerow([command, expected_result, response, status])
        print(f"Product: TRM240 | Command: {command} | Passed: {passed_commands} | Failed: {failed_commands} | Total: {total_commands}")

ser.close()

# Display final summary
print(f"Test Summary - {Fore.GREEN} Passed: {passed_commands} |{Fore.RED} Failed: {failed_commands} |{Style.RESET_ALL} Total: {total_commands}")
