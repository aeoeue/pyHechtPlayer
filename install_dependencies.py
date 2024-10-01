import subprocess
import sys

def install_package(package):
    """Helper function to install a package via pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def install_from_requirements():
    """Install dependencies from the requirements.txt file"""
    try:
        print("Installing dependencies from requirements_pyHechtPlayer.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_pyHechtPlayer.txt"])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print("Failed to install dependencies from requirements_pyHechtPlayer.txt.")
        print(e)

def install_tkinter():
    """Install Tkinter (if not already installed)"""
    try:
        import tkinter
        print("Tkinter is already installed.")
    except ImportError:
        print("Installing Tkinter...")
        if sys.platform.startswith('linux'):
            subprocess.check_call(["sudo", "apt-get", "install", "python3-tk"])
        elif sys.platform == "darwin":
            print("On macOS, Tkinter should come pre-installed with Python.")
        elif sys.platform == "win32":
            print("On Windows, Tkinter comes pre-installed with Python.")

if __name__ == "__main__":
    install_tkinter()
    install_from_requirements()
