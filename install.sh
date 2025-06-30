#!/bin/bash

echo "Installing Spring Boot Unit Test Generator Dependencies"
echo "====================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not available"
    echo "Please ensure pip3 is installed and try again"
    exit 1
fi

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "====================================================="
echo "Installation completed successfully!"
echo "====================================================="
echo ""
echo "Next steps:"
echo "1. Set your Google Gemini AI API key:"
echo "   export GEMINI_API_KEY='your-api-key-here'"
echo ""
echo "2. Run the tool:"
echo "   python3 main.py --help"
echo ""
echo "3. Or try the examples:"
echo "   python3 examples.py"
echo ""
