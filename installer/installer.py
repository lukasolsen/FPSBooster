import tkinter as tk
import os
import subprocess
import shutil
import requests
import zipfile
import urllib.request
import sys
import threading
import time


class EnsureInstallers:
    def __init__(self):
        self.hasPython = False
        self.hasPip = False
        self.hasRequirements = False
        self.hasGithub = False

        self.install_python()
        self.install_pip()

    def install_python(self):
        """Install Python if it's not already installed."""
        if not shutil.which("python"):
            # Install python
            print("Python not found. Installing Python...")

            python_version = "3.9.6"  # Python version
            system_architecture = "64" if sys.maxsize > 2**32 else "32"

            # Define the url:
            python_url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}-amd{system_architecture}-embed.exe"
            install_dir = os.path.join(
                os.environ["PROGRAMFILES"], "Python", python_version)

            if os.path.exists(install_dir):
                print(
                    f"Python {python_version} is already installed in {install_dir}")
                self.hasPython = True

            try:
                print(f"Downloading Python from {python_url}...")
                urllib.request.urlretrieve(python_url, "python_installer.exe")
            except urllib.error.URLError as e:
                print(f"Error downloading Python: {e}")
                sys.exit(1)

            # Install Python
            try:
                print(f"Installing Python {python_version}...")
                subprocess.run(
                    ["python_installer.exe", "/quiet", "TargetDir=" + install_dir])
                print(
                    f"Python {python_version} installed successfully in {install_dir}")
            except Exception as e:
                print(f"Failed to install Python: {e}")
                sys.exit(1)

            os.remove("python_installer.exe")
            self.hasPython = True
        else:
            self.hasPython = True
            print("Python is already installed.")

    def install_pip(self):
        """Install pip if it's not already installed."""
        if not shutil.which("pip"):
            print("pip not found. Installing pip...")
            subprocess.run(
                ["python", "-m", "ensurepip", "--upgrade"], shell=True)
            print("pip installed successfully.")
            self.hasPip = True
        else:
            print("pip is already installed.")
            self.hasPip = True

    def install_requirements(self, directory):
        """Install Python requirements from requirements.txt in a specified directory."""
        requirements_path = os.path.join(directory, "requirements.txt")
        if os.path.exists(requirements_path):
            print("Installing requirements...")
            subprocess.run(["pip", "install", "-r", requirements_path])
            print("Requirements installed successfully.")
            self.hasRequirements = True
        else:
            print("requirements.txt not found. Skipping installation.")
            self.hasRequirements = False

    def check_directory(self, path):
        """Check if a directory exists and is not empty."""
        return os.path.exists(path) and any(os.listdir(path))

    def fetch_github_repository(self, url, directory):
        """Fetch a GitHub repository and extract it to a directory."""
        print(f"Fetching GitHub repository from {url}...")
        try:
            response = requests.get(url + "/archive/main.zip")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GitHub repository: {e}")
            sys.exit(1)

        zip_data = response.content
        # Check if directory exist or not
        if not os.path.exists(directory):
            os.makedirs(directory)
        zip_file_path = os.path.join(directory, "repository.zip")

        with open(zip_file_path, "wb") as zip_file:
            zip_file.write(zip_data)

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(directory)

        os.remove(zip_file_path)

        print("GitHub repository fetched and extracted successfully.")


def run_background_script(directory):
    """Run a Python script in the background."""
    script_path = os.path.join(directory, "main.pyw")
    if os.path.exists(script_path):
        # print("Running background script...")
        subprocess.Popen(["pythonw", script_path])
        # print("Background script is running.")
        print("Success!")
    else:
        print("main.pyw not found. Skipping execution.")


def install_and_run():
    ensure = EnsureInstallers()
    path = os.path.join(os.environ["USERPROFILE"],
                        "Desktop", "python")

    if not ensure.check_directory(path):
        ensure.fetch_github_repository(
            "https://github.com/lukasolsen/FPSBooster", path)
        print("Installing requirements...")
        ensure.install_requirements(path + "/FPSBooster-main")
        run_background_script(path + "/FPSBooster-main")
    else:
        print("Directory " + path +
              " exists and is not empty. Skipping installation.")


# GUI
root = tk.Tk()
root.title("FPSBooster Installer")
canvas = tk.Canvas(root, width=400, height=300)
canvas.pack()

title = tk.Label(root, text="FPSBooster Installer", font=(
    "Arial", 20), fg="black")

title.pack()

canvas.create_window(200, 25, window=title)

install_button = tk.Button(root, text="Install", command=install_and_run)
install_button.pack()

root.mainloop()
