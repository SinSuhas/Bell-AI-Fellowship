# 🐰 Habit Rabbit - Daily Habit Tracker

A simple and intuitive daily habit tracker application built with FastAPI backend and Streamlit frontend. Track your habits, visualize progress, and build consistency in your daily routines.

## 🏗️ Architecture & Approach

### System Architecture

```
┌─────────────────┐    HTTP Requests    ┌──────────────────┐
│                 │ ───────────────────► │                  │
│  Streamlit      │                      │   FastAPI        │
│  Frontend       │ ◄─────────────────── │   Backend        │
│  (Port 8501)    │    JSON Responses    │   (Port 8000)    │
└─────────────────┘                      └──────────────────┘
                                                   │
                                                   │
                                                   ▼
                                         ┌──────────────────┐
                                         │   SQLite         │
                                         │   Database       │
                                         │   (habits.db)    │
                                         └──────────────────┘
```

### Technology Stack

**Backend (FastAPI)**
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM for database operations
- **SQLite**: Lightweight, serverless database
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI

**Frontend (Streamlit)**
- **Streamlit**: Framework for building data applications
- **Requests**: HTTP library for API communication
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualization library

### Design Principles

1. **Simplicity First**: Clean, minimal interface focusing on core functionality
2. **RESTful API**: Standard HTTP methods and status codes
3. **Separation of Concerns**: Clear separation between frontend and backend
4. **Data Persistence**: SQLite database for reliable data storage
5. **Real-time Updates**: Live synchronization between UI and database

## 🚀 Features

### Core Functionality
- ✅ Create and manage daily habits
- 📅 Mark habits as complete/incomplete for each day
- 📊 View progress analytics and trends
- 🗑️ Delete habits when no longer needed
- 📈 Visual charts showing completion patterns

### User Interface
- 🏠 **Today's Habits**: Quick view of today's habits with one-click completion
- 📊 **Analytics**: Detailed progress tracking with charts and statistics
- ⚙️ **Manage Habits**: Add, view, and delete habits

## 📦 Project Structure

```
Habit Rabbit/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── habits.db           # SQLite database (auto-generated)
├── frontend/
│   ├── app.py              # Streamlit application
│   └── requirements.txt    # Python dependencies
├── deployment/
│   ├── backend_deploy.sh   # Backend deployment script
│   └── nginx.conf          # Nginx configuration
└── README.md               # This file
```

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
```

2. Create virtual environment:
```bash
python -m venv venv
```

3. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the Streamlit app:
```bash
streamlit run app.py
```

The web application will be available at `http://localhost:8501`

## 🔌 API Endpoints

### Habits Management
- `GET /habits/` - Get all habits
- `POST /habits/` - Create a new habit
- `DELETE /habits/{habit_id}` - Delete a habit
- `GET /habits/today` - Get today's habits with completion status
- `POST /habits/{habit_id}/complete` - Toggle habit completion for today
- `GET /habits/{habit_id}/history` - Get habit completion history

### Example API Usage

**Create a new habit:**
```bash
curl -X POST "http://localhost:8000/habits/" \
     -H "Content-Type: application/json" \
     -d '{"name": "Drink 8 glasses of water", "description": "Stay hydrated"}'
```

**Mark habit as complete:**
```bash
curl -X POST "http://localhost:8000/habits/1/complete"
```

## 🗄️ Database Schema

### Habits Table
- `id`: Primary key (Integer)
- `name`: Habit name (String)
- `description`: Optional description (String)
- `created_date`: Date when habit was created (Date)

### Habit Entries Table
- `id`: Primary key (Integer)
- `habit_id`: Foreign key to habits table (Integer)
- `date`: Date of the entry (Date)
- `completed`: Whether habit was completed (Boolean)
- `created_at`: Timestamp when entry was created (DateTime)

## 🎯 Usage Guide

1. **Start both servers** (backend on :8000, frontend on :8501)
2. **Add habits** using the "Manage Habits" page
3. **Track daily progress** on the "Today's Habits" page
4. **View analytics** to see trends and completion rates
5. **Manage existing habits** by editing or deleting them

## 🚀 Production Considerations

For production deployment, consider:

1. **Database**: Migrate from SQLite to PostgreSQL or MySQL
2. **Authentication**: Add user authentication and authorization
3. **Rate Limiting**: Implement API rate limiting
4. **Logging**: Add comprehensive logging
5. **Error Handling**: Enhanced error handling and user feedback
6. **Testing**: Add unit and integration tests
7. **Caching**: Implement caching for better performance
8. **HTTPS**: Use SSL/TLS encryption
9. **Environment Variables**: Use environment-based configuration
10. **Backup**: Implement database backup strategies

## 🐛 Troubleshooting

**Backend not starting:**
- Check if port 8000 is already in use
- Verify all dependencies are installed
- Check Python version compatibility

**Frontend cannot connect to backend:**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify API_BASE_URL in frontend/app.py

**Database issues:**
- SQLite database is created automatically
- Check file permissions in the backend directory
- Ensure sufficient disk space

## 📈 Future Enhancements

- 📱 Mobile-responsive design
- 🔔 Push notifications and reminders
- 📅 Calendar integration
- 🎯 Habit streaks and achievements
- 👥 Social features and sharing
- 📊 Advanced analytics and insights
- 🔄 Data import/export functionality
- 🌙 Dark mode theme
- 📝 Notes and reflections for each habit
- ⏰ Custom reminder times

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ for building better habits! 🐰**
