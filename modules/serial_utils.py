import serial
import subprocess

def connect_to_device(port, baudrate, timeout):
    # Stop ModemManager service
    subprocess.run(['sudo', 'systemctl', 'stop', 'ModemManager'])

    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        return ser
    except serial.SerialException as e:
        print(f"Error: Failed to connect to the device. {e}")
        return None
