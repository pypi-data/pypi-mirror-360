#!/bin/bash

echo "========================================"
echo "       QUIZR Installation Script"
echo "========================================"
echo
echo "This will install QUIZR and its dependencies."
echo
read -p "Press Enter to continue..."

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python first:"
        echo "  macOS: brew install python3 or download from python.org"
        echo "  Linux: sudo apt install python3 python3-pip (Ubuntu/Debian)"
        echo "         sudo yum install python3 python3-pip (CentOS/RHEL)"
        echo "         sudo pacman -S python python-pip (Arch)"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Python found!"
echo

echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    if ! command -v pip &> /dev/null; then
        echo "ERROR: pip is not installed"
        echo "Please install pip first:"
        echo "  macOS: python3 -m ensurepip --upgrade"
        echo "  Linux: sudo apt install python3-pip (Ubuntu/Debian)"
        exit 1
    else
        PIP_CMD="pip"
    fi
else
    PIP_CMD="pip3"
fi

echo "pip found!"
echo

echo "Installing dependencies..."
$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "You might need to run: sudo $PIP_CMD install -r requirements.txt"
    exit 1
fi

echo
echo "Installing QUIZR..."
$PIP_CMD install -e .
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install QUIZR"
    echo "You might need to run: sudo $PIP_CMD install -e ."
    exit 1
fi

echo
echo "========================================"
echo "      Installation Complete!"
echo "========================================"
echo
echo "You can now use QUIZR with:"
echo "  $PYTHON_CMD -m quizr list"
echo "  $PYTHON_CMD -m quizr start network+ quick"
echo "  $PYTHON_CMD -m quizr progress"
echo

echo "Testing installation..."
$PYTHON_CMD -m quizr --help > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "WARNING: Installation may have issues"
else
    echo "✓ QUIZR installed successfully!"
fi

echo
echo "Making install script executable for future use..."
chmod +x install.sh

echo "Installation complete! Press Enter to exit..."
read 