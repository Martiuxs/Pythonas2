import os
from colorama import Fore, Style

def expected_return(command, expected_result, response):
    try:
        resultFound = response.find(expected_result)
        if resultFound != -1:
            return f"\rTesting Command {command} | Command: Passed | Expected results: {expected_result} | Received Results: {response[resultFound:len(response)]}"
        else:
            return f"\rTesting Command {command} | Command: Failed | Expected results: {expected_result} | Received Results: {response.strip()}"
    except (TypeError, ValueError) as e:
        return f"\rTesting Command {command} | Command: Failed | Expected results: {expected_result} | Received Results: {response.strip()}"

def move(y, x):
    print("\033[%d;%dH" % (y, x))
