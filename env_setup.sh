#!/bin/bash

# Exit immediately on error
set -e

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Virtual environment setup complete."
echo "To activate it later, run:"
echo "source venv/bin/activate"
