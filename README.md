# JaManager

A modern, real-time jam session management application built with FastAPI and vanilla JavaScript.

## 🚀 Quick Start

```bash
# Set up Python environment
pyenv install 3.11.11
pyenv virtualenv 3.11.11 jv3.11.11
pyenv activate jv3.11.11

# Install dependencies
pip install -r requirements.txt

# Set up database (using Podman)
podman run --name postgres-jamanger -e POSTGRES_PASSWORD=jamanger123 -e POSTGRES_DB=jamanger -p 5432:5432 -d postgres:15

# Initialize database
python init_db.py

# Start the application
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000` and use access code `admin123` for jam manager privileges.

## 📚 Documentation

- [Requirements](docs/REQUIREMENTS.md) - Detailed feature specifications
- [Test Plan](docs/TEST_PLAN.md) - Comprehensive testing guide
- [Testing Guide](docs/TESTING_GUIDE.md) - How to test the application
- [Session Summary](docs/SESSION_SUMMARY.md) - Development history

## 🎵 Features

- **Real-time Voting**: Vote on songs with live updates
- **Jam Management**: Create and manage jam sessions
- **Venue Management**: Manage multiple venues
- **Performance Registration**: Musicians can register to perform
- **QR Code Access**: Easy sharing of jam sessions
- **Role-based Access**: Anonymous, registered, and manager roles

## 🏗️ Architecture

- **Backend**: FastAPI with PostgreSQL and WebSockets
- **Frontend**: Vanilla JavaScript with responsive design
- **Database**: PostgreSQL with JSONB support
- **Real-time**: WebSocket connections for live updates

## 📁 Project Structure

```
jamanger/
├── main.py              # FastAPI application
├── models.py            # Database models
├── requirements.txt     # Python dependencies
├── static/             # Frontend assets
├── docs/               # Documentation
├── scripts/            # Utility scripts
└── tests/              # Test files
```

## 🔧 Configuration

Create a `.env` file:
```env
DATABASE_URL=postgresql://postgres:jamanger123@localhost:5432/jamanger
ACCESS_CODE=admin123
```

## 🧪 Testing

```bash
# Run automated tests
./scripts/run_tests.sh

# Manual testing
open test_websocket.html
```

## 📄 License

MIT License - see LICENSE file for details.