from modules.serial_utils import connect_to_device
from modules.command_utils import  send_at_commands
from modules.result_utils import write_results_to_csv
from modules.config_utils import load_config
from modules.argparser_utils import parse_arguments
from datetime import datetime
import sys
import time


def main():
    parsed_config = parse_arguments()

    port = parsed_config.get('port')
    baudrate = parsed_config.get('baudrate')
    timeout = parsed_config.get('timeout')
    command_file = parsed_config.get('command_file')
    config_file = parsed_config.get('config_file', 'config.json')

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
    print(f"Total commands to test: {total_commands}")
    time.sleep(0.8)
    responses = send_at_commands(ser, device['commands'])
    write_results_to_csv(file_name, responses, config_file)

    ser.close()

    sys.stdout.write("\n")
    sys.stdout.flush()

if __name__ == '__main__':
    main()
