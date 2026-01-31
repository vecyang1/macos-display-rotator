#!/bin/bash

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Please install Homebrew first."
    exit 1
fi

# Install displayplacer
echo "Checking displayplacer..."
if ! command -v displayplacer &> /dev/null; then
    echo "Installing displayplacer..."
    brew tap jakehilborn/jakehilborn
    brew install displayplacer
else
    echo "displayplacer is already installed."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install rumps pynput

echo "Done!"
