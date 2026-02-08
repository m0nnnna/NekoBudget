"""Build script for NekoBudget - compiles to standalone .exe"""

import subprocess
import sys
import os


def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")


def build_exe():
    """Build the executable using PyInstaller."""
    print("\n" + "=" * 50)
    print("Building NekoBudget.exe")
    print("=" * 50 + "\n")

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",           # Single executable file
        "--windowed",          # No console window (GUI app)
        "--name", "NekoBudget",
        "--clean",             # Clean cache before building
        "--noconfirm",         # Replace output without asking
        "main.py"
    ]

    # Run PyInstaller
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("BUILD SUCCESSFUL!")
        print("=" * 50)
        print(f"\nExecutable location: dist/NekoBudget.exe")
        print("\nNote: The .exe will create 'nekobudget.db' and 'receipts/'")
        print("folder in the same directory where it runs.")
    else:
        print("\n" + "=" * 50)
        print("BUILD FAILED!")
        print("=" * 50)
        sys.exit(1)


def main():
    print("=" * 50)
    print("NekoBudget Build Script")
    print("=" * 50)

    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Check for required files
    if not os.path.exists("main.py"):
        print("Error: main.py not found!")
        sys.exit(1)

    if not os.path.exists("database.py"):
        print("Error: database.py not found!")
        sys.exit(1)

    # Install PyInstaller if needed
    install_pyinstaller()

    # Build the executable
    build_exe()


if __name__ == "__main__":
    main()
