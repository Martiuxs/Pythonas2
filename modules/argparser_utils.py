import argparse
from modules.config_utils import load_config

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--baudrate', help='Baud rate', type=int)
    parser.add_argument('--timeout', help='Serial timeout', type=float)
    parser.add_argument('--command-file', help='Command file', default='Commands.json')
    parser.add_argument('--config-file', help='Config file', default='config.json')

    args = parser.parse_args()

    config_file = args.config_file
    config = load_config(config_file)
    
    # Overwrite config values with command-line arguments, if provided
    config['port'] = args.port or config.get('port', '/dev/ttyUSB2')
    config['baudrate'] = args.baudrate or config.get('baudrate', 115200)
    config['timeout'] = args.timeout or config.get('timeout', 1.0)
    config['command_file'] = args.command_file

    return config
