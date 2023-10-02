import tkinter as tk
import os
import subprocess
import shutil
import requests
import zipfile
import sys
import threading


def check_directory(path):
    """Check if a directory exists and is not empty."""
    return os.path.exists(path) and any(os.listdir(path))


def install_python():
    """Install Python if it's not already installed."""
    if not shutil.which("python"):
        print("Python not found. Installing Python...")
        subprocess.run(["python", "get-pip.py"], shell=True)
        print("Python installed successfully.")
    else:
        print("Python is already installed.")


def install_requirements(directory):
    """Install Python requirements from requirements.txt in a specified directory."""
    requirements_path = os.path.join(directory, "requirements.txt")
    if os.path.exists(requirements_path):
        print("Installing requirements...")
        subprocess.run(["pip", "install", "-r", requirements_path])
        print("Requirements installed successfully.")
    else:
        print("requirements.txt not found. Skipping installation.")


def fetch_github_repository(url, directory):
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
        print("Running background script...")
        subprocess.Popen(["pythonw", script_path])
        print("Background script is running.")
    else:
        print("main.pyw not found. Skipping execution.")


def install_and_run():
    install_python()
    if not check_directory("C:\\Users\\lukma\\Desktop\\python"):
        fetch_github_repository(
            "https://github.com/lukasolsen/FPSBooster", "C:\\Users\\lukma\Desktop\\python")
        install_requirements("C:/Users/lukma/Desktop/python/FPSBooster-main")
        run_background_script("C:/Users/lukma/Desktop/python/FPSBooster-main")
    else:
        print("Directory C:/Users/lukma/Desktop/python exists and is not empty. Skipping installation.")


# GUI
root = tk.Tk()
root.title("Installer")
canvas = tk.Canvas(root, width=400, height=300)
canvas.pack()

install_button = tk.Button(root, text="Install", command=install_and_run)
install_button.pack()

root.mainloop()
