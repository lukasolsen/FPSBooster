import socket
import threading
import time


class FileTransfer():
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
                print(f"File Upload -> Error connecting: {str(e)}")
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
                print("Waiting for file...")
                # Get the file name from the server.
                file_name = self.s.recv(1024).decode()
                if not file_name:
                    break

                print("File Name -> ", file_name)

                # Get the file size from the server.
                file_size = int(self.s.recv(1024).decode())
                print("File Size -> ", file_size)

                self.make_file(file_name, file_size)
                print("File received successfully.")
            except Exception as e:
                print("Error handling client. ->", e)
                break
        pass

    def make_file(self, file_name, file_size):
        print("Making file...")
        """Receive a file from the server."""

        # Create a new file with the same name as the one sent by the server.
        with open(file_name, "wb") as file:
            # Keep receiving data from the server until we have received the entire file.
            print("Opening file...")
            while file_size > 0:
                print("Receiving file...")
                # Receive 1024 bytes of data from the server.
                file_data = b""
                done = False

                while not done:
                    if file_data[-7:] == b"<ENDOF>":
                        print("Done receiving file...")
                        done = True

                    else:
                        print("Continuing to receive file...")

                        data = self.s.recv(4096)
                        file_data += data  # Accumulate data in file_data

                print("Writing file...")
                # Write the accumulated data to the file.
                file.write(file_data)  # Write file_data, not data

                # Subtract the number of bytes received from the file size.
                # Update file_size with the length of file_data
                file_size -= len(file_data)

        print(f"File received: {file_name}")
        # send a message to the server to let it know that we have received the file.
        self.s.send("OK".encode())
