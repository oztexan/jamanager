#!/bin/bash

# Jamanager Development Environment Setup Script
# This script sets up a complete development environment for Jamanager

set -e  # Exit on any error

echo "🚀 Jamanager Development Environment Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Please run this script from the jamanager root directory"
    exit 1
fi

print_status "Setting up Jamanager development environment..."

# Check Python version
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if pyenv is available
if command -v pyenv &> /dev/null; then
    print_status "Pyenv found, checking for jv3.11.11 environment..."
    if pyenv versions | grep -q "jv3.11.11"; then
        print_success "Pyenv environment jv3.11.11 found"
        print_status "Activating pyenv environment..."
        export PYENV_VERSION="jv3.11.11"
        eval "$(pyenv init -)"
    else
        print_warning "Pyenv environment jv3.11.11 not found, using system Python"
    fi
else
    print_warning "Pyenv not found, using system Python"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip
print_success "Pip upgraded"

# Install dependencies
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed from requirements.txt"
else
    print_warning "requirements.txt not found, installing basic dependencies..."
    pip install fastapi uvicorn sqlalchemy python-dotenv
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# Jamanager Environment Configuration
DATABASE_URL=sqlite+aiosqlite:///./jamanager.db
JAM_MANAGER_ACCESS_CODE=jam2024

# Development settings
DEBUG=True
LOG_LEVEL=INFO

# Optional: Custom settings
# UPLOAD_DIR=./uploads
# MAX_FILE_SIZE=10485760
EOF
    print_success ".env file created with default settings"
else
    print_success ".env file already exists"
fi

# Initialize database
print_status "Initializing database..."
if [ -f "init_dev_database.py" ]; then
    python init_dev_database.py
    print_success "Database initialized with development data"
else
    print_warning "init_dev_database.py not found, database will be created on first run"
fi

# Create uploads directory
print_status "Creating uploads directory..."
mkdir -p uploads
print_success "Uploads directory created"

# Check if the application can start
print_status "Testing application startup..."
if python -c "import main; print('Application imports successfully')" 2>/dev/null; then
    print_success "Application imports successfully"
else
    print_error "Application import failed"
    exit 1
fi

# Create helpful aliases
print_status "Creating development aliases..."
cat > dev-aliases.sh << 'EOF'
#!/bin/bash
# Jamanager Development Aliases
# Source this file to use: source dev-aliases.sh

alias jamanager-dev="cd /Users/chrisrobertson/dev/jamanager && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 3000 --reload"
alias jamanager-test="cd /Users/chrisrobertson/dev/jamanager && source venv/bin/activate && python -m pytest tests/ -v"
alias jamanager-lint="cd /Users/chrisrobertson/dev/jamanager && source venv/bin/activate && python -m flake8 ."
alias jamanager-format="cd /Users/chrisrobertson/dev/jamanager && source venv/bin/activate && python -m black ."
alias jamanager-reset-db="cd /Users/chrisrobertson/dev/jamanager && source venv/bin/activate && python reset_dev_database.py"

echo "Jamanager development aliases loaded!"
echo "Available commands:"
echo "  jamanager-dev     - Start development server on port 3000"
echo "  jamanager-test    - Run tests"
echo "  jamanager-lint    - Run linting"
echo "  jamanager-format  - Format code"
echo "  jamanager-reset-db - Reset development database"
EOF

chmod +x dev-aliases.sh
print_success "Development aliases created (source dev-aliases.sh to use)"

# Final status
echo ""
print_success "🎉 Jamanager development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Start the development server:"
echo "   source venv/bin/activate"
echo "   python -m uvicorn main:app --host 0.0.0.0 --port 3000 --reload"
echo ""
echo "2. Or use the convenient alias:"
echo "   source dev-aliases.sh"
echo "   jamanager-dev"
echo ""
echo "3. Access the application at:"
echo "   http://localhost:3000"
echo ""
echo "4. For jam manager access, use access code: jam2024"
echo ""
print_success "Happy coding! 🎵"
