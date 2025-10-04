# JaManager

A modern, real-time jam session management application built with FastAPI and vanilla JavaScript. JaManager allows musicians to create jam sessions, manage song queues, vote on songs, and register to perform - all with real-time updates via WebSockets.

## 🏗️ Project Structure

This project follows modern best practices with a server-rendered architecture:

```
jamanager/
├── backend/                 # FastAPI backend application
│   ├── app/                # Main application code
│   │   ├── api/           # API endpoints and dependencies
│   │   ├── core/          # Core application components
│   │   ├── models/        # Database models and schemas
│   │   ├── services/      # Business logic services
│   │   ├── utils/         # Utility functions
│   │   └── static/        # Static files (served by FastAPI)
│   ├── tests/             # Backend tests
│   ├── requirements.txt   # Python dependencies
│   └── pyproject.toml     # Python project configuration
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── config/                # Configuration files
├── docker-compose.yml     # Docker Compose configuration
└── Makefile              # Development commands
```

## 🚀 Quick Start

### Database Initialization

The development database comes pre-populated with 30 popular cover songs including:
- **Dreams** by Fleetwood Mac
- **Valerie** by Amy Winehouse  
- Classic rock hits (Sweet Child O' Mine, Hotel California, Wonderwall, etc.)
- Pop favorites (I Will Survive, Dancing Queen, Billie Jean, etc.)
- Alternative/Indie tracks (Creep, Mr. Brightside, Ho Hey, etc.)
- Country/Folk songs (Wagon Wheel, Tennessee Whiskey, Jolene, etc.)
- Blues/Soul classics (Ain't No Sunshine, Georgia on My Mind, etc.)
- Modern pop hits (Shallow, Perfect, Shape of You, etc.)

To reset the development database with this song set:
```bash
python reset_dev_database.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd jamanager

# Install all dependencies
make install

# Initialize the database
make setup-db

# Start development servers
make dev
```

This will start:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

### Alternative: Docker

```bash
# Build and start with Docker Compose
make docker-build
make docker-up
```

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

## 🛠️ Development

### Available Commands

```bash
make help                 # Show all available commands
make install              # Install all dependencies
make dev                  # Start both backend and frontend
make dev-backend          # Start only backend
make dev-frontend         # Start only frontend
make test                 # Run all tests
make lint                 # Run linting
make format               # Format code
make build                # Build for production
make clean                # Clean build artifacts
```

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```


## 🧪 Testing

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

```

## 🔧 Configuration

Create a `.env` file in the project root:

```env
DATABASE_URL=sqlite+aiosqlite:///./backend/data/jamanager.db
JAM_MANAGER_ACCESS_CODE=jam2024
```

## 📚 Documentation

- [Requirements](docs/REQUIREMENTS.md) - Detailed feature specifications
- [Test Plan](docs/TEST_PLAN.md) - Comprehensive testing guide
- [Testing Guide](docs/TESTING_GUIDE.md) - How to test the application
- [Session Summary](docs/SESSION_SUMMARY.md) - Development history

## 🏗️ Architecture

- **Backend**: FastAPI with SQLite and WebSockets
- **Frontend**: Server-rendered HTML with vanilla JavaScript modules
- **Database**: SQLite with JSON support (file-based, zero configuration)
- **Real-time**: WebSocket connections for live updates
- **Build System**: setuptools for backend
- **Containerization**: Docker and Docker Compose support

## 📄 License

MIT License - see LICENSE file for details.