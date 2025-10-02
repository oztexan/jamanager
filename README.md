# JaManager

A modern, real-time jam session management application built with FastAPI and vanilla JavaScript. JaManager allows musicians to create jam sessions, manage song queues, vote on songs, and register to perform - all with real-time updates via WebSockets.

## 🚀 Quick Start

```bash
# Set up Python environment
pyenv install 3.11.11
pyenv virtualenv 3.11.11 jv3.11.11
pyenv activate jv3.11.11

# Install dependencies
pip install -r requirements.txt

# Initialize database (SQLite - no external setup required)
python init_sqlite_db.py

# Start the application
python start_fresh.py
```

Visit `http://localhost:8000` and use access code `jam2024` for jam manager privileges.

## 📚 Documentation

- [Requirements](docs/REQUIREMENTS.md) - Detailed feature specifications
- [Test Plan](docs/TEST_PLAN.md) - Comprehensive testing guide
- [Testing Guide](docs/TESTING_GUIDE.md) - How to test the application
- [Session Summary](docs/SESSION_SUMMARY.md) - Development history

## 🎵 Features

### For All Users
- **Real-time Voting**: Vote on songs with live updates across all connected devices
- **Song Queue Management**: Songs are automatically ordered by vote count (highest first)
- **Anonymous Participation**: Join and vote without registration
- **Responsive Design**: Works on desktop and mobile devices
- **QR Code Access**: Easy sharing via QR codes for jam sessions
- **Ultimate Guitar Integration**: Automatic chord sheet lookup for songs

### For Registered Attendees (Musos)
- **Performance Registration**: Register to perform on specific songs
- **Attendee Persistence**: Stay logged in across browser sessions
- **Performance Management**: Unregister from songs when needed

### For Jam Managers
- **Jam Creation**: Create jam sessions with custom names, venues, dates, and background images
- **Venue Management**: Manage multiple venues for your jam sessions
- **Access Control**: Secure access via access codes
- **Real-time Monitoring**: Monitor jam activity and song queues
- **Breadcrumb Navigation**: Easy navigation between management areas
- **Full Voting Rights**: Can vote on songs like any other user

## 🏗️ Architecture

- **Backend**: FastAPI with SQLite and WebSockets
- **Frontend**: Vanilla JavaScript with responsive design
- **Database**: SQLite with JSON support (file-based, zero configuration)
- **Real-time**: WebSocket connections for live updates
- **IDs**: String-based IDs for better compatibility

## 📁 Project Structure

```
jamanager/
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
DATABASE_URL=sqlite+aiosqlite:///./jamanager.db
JAM_MANAGER_ACCESS_CODE=jam2024
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