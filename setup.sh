#!/bin/bash

# Exit immediately if a command fails
set -e


# Step 1: Create virtual environment
echo "[+] Creating virtual environment 'venv'..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[-] Error: Python 3 is not installed or not in PATH"
    echo "    Please install Python 3 and try again"
    exit 1
fi

# Check if venv directory already exists
if [ -d "venv" ]; then
    echo "[!] Warning: 'venv' directory already exists"
    read -p "    Do you want to remove it and create a new one? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "[+] Removing existing 'venv' directory..."
        rm -rf venv
    else
        echo "[-] Setup aborted by user"
        exit 1
    fi
fi

# Create virtual environment
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[-] Failed to create virtual environment"
    echo "    Please ensure Python 3 and venv module are installed:"
    echo "    - On Ubuntu/Debian: sudo apt-get install python3-venv"
    echo "    - On Fedora: sudo dnf install python3-venv"
    echo "    - On macOS: pip3 install virtualenv"
    exit 1
fi

# Step 2: Activate virtual environment
echo "[+] Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    if [ $? -ne 0 ] || [ -z "$VIRTUAL_ENV" ]; then
        echo "[-] Failed to activate virtual environment"
        exit 1
    fi
    echo "[✓] Virtual environment activated successfully"
else
    echo "[-] Virtual environment activation script not found"
    echo "    Expected at: venv/bin/activate"
    exit 1
fi

# Install required packages
echo "[+] Installing required packages..."
pip install --upgrade pip >/dev/null || { echo "[-] Failed to upgrade pip"; exit 1; }
echo "[✓] Pip upgraded successfully"

# Install required packages with progress feedback
echo "[+] Installing pyverilog..."
pip install pyverilog || { echo "[-] Failed to install pyverilog"; exit 1; }
echo "[✓] Installed pyverilog successfully"

echo "[+] Installing networkx..."
pip install networkx || { echo "[-] Failed to install networkx"; exit 1; }
echo "[✓] Installed networkx successfully"

# Optional packages - ask user if they want to install
read -p "[?] Install matplotlib for graph visualization? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[+] Installing matplotlib..."
    pip install matplotlib || echo "[!] Warning: matplotlib installation failed, continuing anyway"
    echo "[✓] Installed matplotlib successfully"
fi

# Freeze the environment
echo "[+] Freezing installed packages to requirements.txt..."
pip freeze > requirements.txt || { echo "[-] Failed to create requirements.txt"; exit 1; }
echo "[✓] Created requirements.txt successfully"

echo "[✓] Setup complete. Environment 'venv' is ready and activated."
echo "To activate it again later: source venv/bin/activate"
echo "To deactivate: deactivate"
echo "You can now run the script using: python main.py --parse -i <input_filename.v> -o <outputfilename.txt> "
echo "or: python main.py --scoap -i <input_filename.v> -o <outputfilename.json |txt> "
echo "For more details, check the README.md file."
