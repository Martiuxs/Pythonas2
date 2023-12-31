import serial
import csv
from datetime import datetime
from colorama import Fore, Style
import json
import sys
import time
import os
import subprocess
import argparse

def load_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            return config
    except json.JSONDecodeError:
        raise ValueError(f"Error: Invalid JSON format in {file_path}")

def connect_to_device(port, baudrate, timeout):
    # Stop ModemManager service
    subprocess.run(['sudo', 'systemctl', 'stop', 'ModemManager'])

    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        return ser
    except serial.SerialException as e:
        print(f"Error: Failed to connect to the device. {e}")
        return None

def move(y, x):
    print("\033[%d;%dH" % (y, x))

def expected_return(command, expected_result, response):
    try:
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

        os.system("clear")
        sys.stdout.write(f"\r{expected_return(command, expected_result, response)}")
        sys.stdout.flush()

        if response.find(expected_result) != -1:
            passed_commands += 1
        else:
            failed_commands += 1

        move(5, 0)
        sys.stdout.write(f"{' ' * 30}Test Summary - {Fore.GREEN}Passed: {passed_commands} |{Fore.RED} Failed: {failed_commands} |{Style.RESET_ALL} Total: {passed_commands + failed_commands}")
        sys.stdout.flush()

    sys.stdout.write("\n")
    sys.stdout.flush()
    return responses

def write_results_to_csv(file_name, results, config_file):
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--baudrate', help='Baud rate', type=int)
    parser.add_argument('--timeout', help='Serial timeout', type=float)
    parser.add_argument('--command-file', help='Command file', default='Commands.json')
    parser.add_argument('--config-file', help='Config file', default='config.json')

    args = parser.parse_args()

    config = load_config(args.config_file)
    port = args.port or config.get('port', '/dev/ttyUSB2')
    baudrate = args.baudrate or config.get('baudrate', 115200)
    timeout = args.timeout or config.get('timeout', 1.0)
    command_file = args.command_file
    config_file = args.config_file

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

    ser = connect_to_device(port, baudrate, timeout)

    if ser is None:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{product_name}_{timestamp}.csv"

    total_commands = len(device['commands'])
    responses = send_at_commands(ser, device['commands'])
    write_results_to_csv(file_name, responses, config_file)

    ser.close()

    sys.stdout.write("\n")
    sys.stdout.flush()

if __name__ == '__main__':
    main()
