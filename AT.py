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

def connect_to_device(config_file):
    config = load_config(config_file)
    try:
        device_port = config['port']
        baud_rate = config['baudrate']
        timeout = config['timeout']

        ser = serial.Serial(device_port, baud_rate, timeout=timeout)
        return ser
    except serial.SerialException as e:
        print(f"Error: Failed to connect to the device. {e}")
        return None
 
def move (y, x):
    print("\033[%d;%dH" % (y, x))
       
def expected_return(command, expected_result, response):
    try :
        resultFound = response.find(expected_result)
        if resultFound != -1:
            return f"\rTesting Command {command} | Command: Passed | Expected results: {expected_result} | Received Results: {response[resultFound:len(response)]}"
        else:
            return f"\rTesting Command {command} | Command: Failed | Expected results: {expected_result} | Received Results: {response.strip()}"
    except (TypeError, ValueError) as e:
        return f"\rTesting Command {command} | Command: Failed | Expected results: {expected_result} | Received Results: {response.strip()}"
        
def send_at_commands(ser, commands):
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

def write_results_to_csv(file_name, results,config_file):
    config = load_config(config_file)
    folder_path = config['folder_path']
    
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Command ', 'Expected Result ', 'Received Result ', 'Status '])
        for command, expected_result, response in results:
            if response.find(expected_result) != -1:
                status = 'Passed'
            else:
                status = 'Failed'
            writer.writerow([command.ljust(5), expected_result.ljust(5), response, status])

def run_at_command_tests(command_file, product_name):
    data = load_config(command_file)
    config = load_config(config_file)
    
    product_name = config.get('product_name')
    
    if product_name is None:
        print("Product name not found in the configuration.")
        return
    
    device = None

    for d in data['devices']:
        if d['device'] == product_name:
            device = d
            break

    if device is None:
        print(f"Product '{product_name}' not found in the configuration.")
        return

    ser = connect_to_device(config_file)

    if ser is None:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{product_name}_{timestamp}.csv"

    total_commands = len(device['commands'])
    responses = send_at_commands(ser, device['commands'])
    write_results_to_csv(file_name, responses,config_file)

    ser.close()

    # Print the final test summary with additional spaces
    sys.stdout.write("\n")
    sys.stdout.flush()

command_file = 'Commands.json'
config_file = 'config.json'

run_at_command_tests(command_file, config_file)

# Received Result and Expected Result and Failed or Passed 3-4 dynamic lines