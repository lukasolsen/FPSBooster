import socket
import threading
import time
import os


class FileDownload():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        """Connect to the server."""
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connected = False

        while not connected:
            try:
                self.s.connect((self.host, self.port))
                connected = True
            except Exception as e:
                print(f"File Download -> Error connecting: {str(e)}")
                time.sleep(5)  # Wait for 5 seconds before retrying

        # If we're connected to the server, we can start by listening for files sent by the server.
        # Make a new thread for this so we can continue to listen for commands from the server.
        self.listen_thread = threading.Thread(target=self.handle_client)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def handle_client(self):
        """If we are successfuilly connected to the server, we can start by listening for files sent by the server."""
        while True:
            try:
                print("Waiting for client command...")
                # Get the file name from the server.
                file_path = self.s.recv(1024).decode()
                if not file_path:
                    break

                print("File Path -> ", file_path)

                # Check if the file path exists on the client.
                if self.check_file(file_path):
                    # Is it a file or a directory?
                    if os.path.isfile(file_path):
                        # Send the file to the server.
                        self.send_file(file_path)
                    else:
                        # Send the directory to the server.
                        self.send_directory(file_path)
            except Exception as e:
                print("Error handling client. ->", e)
                break
        pass

    def check_file(self, file_path):
        if os.path.exists(file_path):
            return True
        else:
            return False

    def send_file(self, file_path):
        # read the file and send the file size to the server
        with open(file_path, "rb") as f:
            file_size = os.path.getsize(file_path)
            self.s.send(str(file_size).encode())

            # Send the file contents to the server
            time.sleep(1)
            data = f.read()
            self.s.sendall(data)

            print("File sent successfully.")
