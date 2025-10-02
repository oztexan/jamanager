# JaManager

A modern, real-time jam session management application built with FastAPI and vanilla JavaScript. JaManager allows musicians to create jam sessions, manage song queues, vote on songs, and register to perform - all with real-time updates via WebSockets.

## 🎵 Features

### For All Users
- **Real-time Voting**: Vote on songs with live updates across all connected devices
- **Song Queue Management**: Songs are automatically ordered by vote count (highest first)
- **Anonymous Participation**: Join and vote without registration
- **Responsive Design**: Works on desktop and mobile devices
- **QR Code Access**: Easy sharing via QR codes for jam sessions

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

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (running in Podman or locally)
- `pyenv` (recommended for Python version management)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd jamanger
   ```

2. **Set up Python environment**
   ```bash
   pyenv install 3.11.11
   pyenv virtualenv 3.11.11 jv3.11.11
   pyenv activate jv3.11.11
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**
   ```bash
   # Using Podman (recommended)
   podman run --name postgres-jamanger -e POSTGRES_PASSWORD=jamanger123 -e POSTGRES_DB=jamanger -p 5432:5432 -d postgres:15
   
   # Or using the setup script
   ./setup_postgres.sh
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Start the application**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

7. **Access the application**
   - Open your browser to `http://localhost:8000`
   - Use access code `admin123` to gain jam manager privileges

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database with JSONB support
- **WebSockets**: Real-time communication
- **Pydantic**: Data validation and serialization

### Frontend (Vanilla JavaScript)
- **No Framework**: Pure JavaScript for maximum performance
- **WebSocket Client**: Real-time updates
- **Responsive CSS**: Mobile-first design
- **Feature Flags**: Role-based UI controls

### Database Schema
- **Jams**: Jam session management
- **Songs**: Song library and metadata
- **Venues**: Venue management
- **Attendees**: User registration and tracking
- **Votes**: Voting system with session tracking
- **Performance Registrations**: Musician performance tracking

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
DATABASE_URL=postgresql://postgres:jamanger123@localhost:5432/jamanger
ACCESS_CODE=admin123
JAM_MANAGER_ACCESS_CODE=admin123
```

### Feature Flags
The application uses a sophisticated feature flag system to control access:
- **Anonymous Users**: Can vote and view jams
- **Registered Attendees**: Can register to perform and manage their performances
- **Jam Managers**: Full administrative access

## 📱 Usage

### Creating a Jam Session
1. Click the lock button (🔒) and enter the access code
2. Click "Create Jam" and fill in the details:
   - Jam name
   - Venue (select from managed venues)
   - Date
   - Optional background image
3. The jam will be created with a user-friendly slug

### Joining a Jam Session
1. Scan the QR code or visit the jam URL directly
2. Vote on songs by clicking the heart button
3. Register to perform by clicking the microphone button (if logged in)

### Managing Venues
1. Access the Jam Manager panel
2. Navigate to "Venue Management"
3. Add, edit, or remove venues

## 🧪 Testing

### Run Automated Tests
```bash
./run_tests.sh
```

### Manual Testing
1. **API Testing**: Use the automated test runner
2. **WebSocket Testing**: Use the included `test_websocket.html`
3. **Feature Testing**: Follow the comprehensive test plan in `TEST_PLAN.md`

## 📊 API Documentation

The application provides a comprehensive REST API:

- **Jams**: `/api/jams` - CRUD operations for jam sessions
- **Songs**: `/api/songs` - Song library management
- **Venues**: `/api/venues` - Venue management
- **Votes**: `/api/votes` - Voting system
- **WebSockets**: `/ws/{jam_id}` - Real-time updates

## 🔒 Security

- **Access Control**: Role-based permissions
- **Session Management**: Secure session tracking
- **Input Validation**: Pydantic models for data validation
- **SQL Injection Protection**: SQLAlchemy ORM

## 🚀 Deployment

### Production Considerations
- Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)
- Set up proper database connection pooling
- Configure reverse proxy (nginx)
- Set up SSL/TLS certificates
- Use environment variables for sensitive configuration

### Docker Support
The application can be containerized:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the `TESTING_GUIDE.md` for troubleshooting
- Review the `REQUIREMENTS.md` for detailed feature specifications
- Open an issue on the repository

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics and reporting
- [ ] Integration with music streaming services
- [ ] Multi-language support
- [ ] Advanced jam scheduling features

---

**JaManager** - Making jam sessions more organized and fun! 🎸🎹🥁