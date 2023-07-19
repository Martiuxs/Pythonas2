import csv
import os
from modules.config_utils import load_config

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
