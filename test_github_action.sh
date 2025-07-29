#!/bin/bash

# Test script to simulate GitHub Actions environment locally
echo "=== CRIMENET GitHub Actions Test ==="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi
echo "✅ Python3 found"

# Check if virtual environment can be created
echo "Creating virtual environment..."
python3 -m venv test_venv
source test_venv/bin/activate

# Check if requirements can be installed
echo "Installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Requirements installed successfully"
else
    echo "❌ Failed to install requirements"
    deactivate
    rm -rf test_venv
    exit 1
fi

# Check if main.py can be run
echo "Testing main.py execution..."
python main.py

if [ $? -eq 0 ]; then
    echo "✅ main.py executed successfully"
else
    echo "❌ main.py execution failed"
    deactivate
    rm -rf test_venv
    exit 1
fi

# Check if output files were created
if [ -f "data/crime_news.csv" ]; then
    echo "✅ crime_news.csv created"
    echo "Headlines found: $(tail -n +2 data/crime_news.csv | wc -l)"
else
    echo "❌ crime_news.csv not created"
fi

if [ -f "log" ]; then
    echo "✅ log file created"
else
    echo "❌ log file not created"
fi

# Cleanup
deactivate
rm -rf test_venv

echo ""
echo "=== Test Complete ==="
echo "The GitHub Action should work correctly if all checks passed ✅"
