# SPDX-License-Identifier: MIT
# Copyright 2021 (c) BayLibre, SAS
# Author: Fabien Parent <fparent@baylibre.com>

from importlib import resources
import platform
import subprocess
import sys

def main():
    run(sys.argv)

def run(argv):
    # Locate the pre-built binary 'bootrom-tool' in Windows or Linux OS.
    exe_path = get_exec_path()
    argv[0] = exe_path

    # Execute it to communicate with Genio SoC boot ROM via USB.
    exec_command(argv)

def check_output(argv):
    # Execute 'bootrom-tool' and redirect STDOUT.
    exe_path = get_exec_path()
    argv[0] = exe_path
    try:
        output = subprocess.check_output(argv, stderr=subprocess.STDOUT)
        return output.decode()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e.output.decode()}")
        return None
    except KeyboardInterrupt:
        print("Aborted.")
        return None

def get_exec_path():
    # Determine the path of the executable based on the OS environment.
    mach = platform.machine().lower()
    system = platform.system().lower()
    bin_name = f'bin/{mach}/{system}/bootrom-tool'
    if system == "windows":
        bin_name += ".exe"

    return resources.files('aiot_bootrom') / bin_name

def exec_command(argv):
    try:
        subprocess.run(argv, check=True)
    except KeyboardInterrupt:
        pass