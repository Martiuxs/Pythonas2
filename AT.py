import serial
import csv
from datetime import datetime
from colorama import Fore, Style
import json
import sys
import time
import os

def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            return config
    except json.JSONDecodeError:
        raise ValueError(f"Error: Invalid JSON format in {file_path}")

def connect_to_device():
    try:
        ser = serial.Serial('/dev/ttyUSB4', 115200, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f"Error: Failed to connect to the device. {e}")
        return None
    
def move (y, x):
    print("\033[%d;%dH" % (y, x))
       
def expected_return(command, expected_result, response):
    resultFound = response.find(expected_result)
    if resultFound != -1:
        return f"\rTesting Command {command} | Command: Passed | Expected results: {expected_result} | Received Results: {response[resultFound:len(response)]}"
    else:
        return f"\rTesting Command {command} | Command: Failed | Expected results: {expected_result} | Received Results: {response.strip()}"

def send_at_commands(ser, commands, total_commands):
    responses = []
    passed_commands = 0
    failed_commands = 0
    for i, command_data in enumerate(commands, 1):
        command = command_data['command']
        expected_result = command_data['expects']



        ser.write(f'{command}\r\n'.encode('ascii'))
        time.sleep(0.4)
        response = ser.read_until(b'OK\r\n').decode('ascii').strip()
        responses.append((command, expected_result, response))
        
        # sys.stdout.write(f"\rTesting command {command_data['command']}...")
        os.system("clear")
        sys.stdout.write(f"\r{expected_return(command, expected_result, response)}")
        # Testing Command AT+CGSN | Command: Passed | Expected results:OK | Received Results: OK turėtu maždaug taip atrodyt kažkas pnš
        sys.stdout.flush()
        
        if response.find(expected_result) != -1:
            passed_commands += 1
        else:
            failed_commands += 1

        # Clear the previous test output

        # Print the updated test summary
        move(5, 0)
        sys.stdout.write(f"{' ' * 30}Test Summary - {Fore.GREEN}Passed: {passed_commands} |{Fore.RED} Failed: {failed_commands} |{Style.RESET_ALL} Total: {passed_commands + failed_commands}")
        sys.stdout.flush()
        
        

    sys.stdout.write("\n")
    sys.stdout.flush()
    return responses

def write_results_to_csv(file_name, results):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Command ', 'Expected Result ', 'Received Result ', 'Status '])
        for command, expected_result, response in results:
            if response.find(expected_result) != -1:
                status = 'Passed' 
            else:
                status = 'Failed' 
            writer.writerow([command.ljust(5), expected_result.ljust(5), response, status])

def run_at_command_tests(config_file, product_name):
    data = load_config(config_file)

    device = None

    for d in data['devices']:
        if d['device'] == product_name:
            device = d
            break

    if device is None:
        print(f"Product '{product_name}' not found in the configuration.")
        return

    ser = connect_to_device()

    if ser is None:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{product_name}_{timestamp}.csv"

    total_commands = len(device['commands'])
    responses = send_at_commands(ser, device['commands'], total_commands)
    write_results_to_csv(file_name, responses)

    ser.close()

    # Counters for passed, failed, and total commands
    passed_commands = sum(1 for _, expected_result, response in responses if response.find(expected_result) != -1)
    failed_commands = len(responses) - passed_commands
    total_commands = len(responses)


    # Print the final test summary with additional spaces
    sys.stdout.write("\n")
    sys.stdout.flush()

config_file = 'Commands.json'
product_name = 'TRM240'

run_at_command_tests(config_file, product_name)

# Received Result and Expected Result and Failed or Passed 3-4 dynamic lines