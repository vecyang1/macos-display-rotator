#!/bin/bash
# Screen Rotator - One-Click Installer & Launcher
# Run this script to install dependencies and start the app

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔄 Screen Rotator Installer"
echo "=========================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install displayplacer
echo "📦 Checking displayplacer..."
if ! command -v displayplacer &> /dev/null; then
    echo "   Installing displayplacer..."
    brew tap jakehilborn/jakehilborn
    brew install displayplacer
else
    echo "   ✅ displayplacer already installed"
fi

# Install Python dependencies
echo "📦 Installing Python packages..."
pip3 install --quiet rumps pynput

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Starting Screen Rotator..."
echo "   (Look for 🔄 in your menu bar)"
echo ""

# Run the app
cd "$SCRIPT_DIR"
python3 screen_rotator.py
