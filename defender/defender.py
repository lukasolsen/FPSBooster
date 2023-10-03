# Turn off windows defender real time protection
import subprocess
import sys
import ctypes

# Make sure that we're running as admin
if not ctypes.windll.shell32.IsUserAnAdmin():
    print("Please run this script as an administrator.")
    sys.exit(1)

try:
    subprocess.run(["sc", "config", "WinDefend", "start=", "disabled"])
    print("Windows Defender service disabled.")

    # Disable real time protection
    try:
        subprocess.run(["powershell", "-Command", "Set-MpPreference",
                        "-DisableRealtimeMonitoring", "$true"])
        print("Windows Defender real time protection disabled.")
    except Exception as e:
        print(f"Failed to disable Windows Defender real time protection: {e}")

    # Disable cloud based protection
    try:
        subprocess.run(["powershell", "-Command", "Set-MpPreference",
                        "-DisableIOAVProtection", "$true"])
        print("Windows Defender cloud based protection disabled.")
    except Exception as e:
        print(
            f"Failed to disable Windows Defender cloud based protection: {e}")

    # Disable behavior monitoring
    try:
        subprocess.run(["powershell", "-Command", "Set-MpPreference",
                        "-DisableBehaviorMonitoring", "$true"])
        print("Windows Defender behavior monitoring disabled.")
    except Exception as e:
        print(f"Failed to disable Windows Defender behavior monitoring: {e}")

    # Disable scanning of archive files
    try:
        subprocess.run(["powershell", "-Command", "Set-MpPreference",
                        "-DisableArchiveScanning", "$true"])
        print("Windows Defender scanning of archive files disabled.")
    except Exception as e:
        print(
            f"Failed to disable Windows Defender scanning of archive files: {e}")

    # Disable scanning of downloads
    try:

        subprocess.run(["powershell", "-Command", "Set-MpPreference",
                        "-DisableScanningDownloads", "$true"])
        print("Windows Defender scanning of downloads disabled.")
    except Exception as e:
        print(f"Failed to disable Windows Defender scanning of downloads: {e}")
except Exception as e:
    print(f"Failed to disable Windows Defender real time protection: {e}")
    sys.exit(1)
