import time
import os
from colorama import Fore, Style
import sys
from modules.display_utils import move
from modules.display_utils import expected_return

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
