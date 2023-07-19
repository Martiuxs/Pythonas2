import argparse
from modules.serial_utils import connect_to_device
from modules.command_utils import  send_at_commands
from modules.result_utils import write_results_to_csv
from modules.config_utils import load_config
from modules.display_utils import expected_return, move
from datetime import datetime
import csv
import sys
import os

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
