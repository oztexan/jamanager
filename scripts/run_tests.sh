#!/bin/bash

# Jamanger Automated Test Runner
# This script runs automated tests for the Jamanger application

echo "🎵 Jamanger Automated Test Runner"
echo "================================="

# Check if server is running
echo "🔍 Checking if server is running..."
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Server is running"
else
    echo "❌ Server is not running. Please start the server first:"
    echo "   cd fastapi-jam-vote && pyenv activate jv3.11.11 && uvicorn main:app --reload --port 8000"
    exit 1
fi

# Check if Python dependencies are available
echo "🔍 Checking Python dependencies..."
if python3 -c "import requests" 2>/dev/null; then
    echo "✅ Python dependencies available"
else
    echo "❌ Missing Python dependencies. Installing..."
    pip3 install requests
fi

# Run the automated tests
echo "🚀 Running automated tests..."
python3 automated_test_runner.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "🎉 All tests completed successfully!"
else
    echo "❌ Some tests failed. Check test_report.md for details."
    exit 1
fi
