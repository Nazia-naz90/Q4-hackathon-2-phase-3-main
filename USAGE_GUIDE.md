# AI Todo Assistant Chatbot - Complete Usage Guide

## Getting Started

### 1. Prerequisites
Make sure you have:
- Python 3.8+
- Virtual environment set up
- All dependencies installed

### 2. Running the Backend Service

The recommended way to start the backend is with uvicorn:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or alternatively:
```bash
cd backend
python main.py
```

### 3. Testing the AI Chatbot

Once the backend is running, you can test the AI chatbot using curl commands:

#### Create a User Account:
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'
```

#### Login to Get JWT Token:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -d "username=testuser&password=testpassword123"
```

#### Chat with AI Assistant:
```bash
curl -X POST "http://localhost:8000/ai/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to buy groceries"}'
```

### 4. Using the Demo Script

For an easy way to test everything, run:
```bash
python demo_ai_chatbot.py
```

This will:
1. Create a test user account
2. Login and get an authentication token
3. Send several sample messages to the AI chatbot
4. Display all responses

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/auth/signup` | POST | Create new user |
| `/auth/login` | POST | Login and get JWT token |
| `/ai/chat` | POST | Chat with AI assistant |
| `/ai/health` | GET | Check AI service status |
| `/tasks` | GET/POST | Manage tasks |

## Common Commands for AI Chatbot

- **Create tasks**: "Create a task to buy groceries", "Add a task to finish the project"
- **List tasks**: "Show my tasks", "List all tasks", "What are my tasks?"
- **Complete tasks**: "Complete task [ID]", "Mark task as done"
- **Delete tasks**: "Delete task [ID]", "Remove task [ID]"
- **Help**: "What can you do?", "Help", "Commands"

## Troubleshooting

### If you get "Connection refused":
Make sure the backend is running:
```bash
curl http://localhost:8000/
```

### If you get authentication errors:
Double-check your username/password and ensure you're using the correct JWT token.

### If you see database errors:
Make sure your database is properly configured and accessible.

## Windows Users

For Windows users, use the batch file:
```cmd
start_services.bat
```

Or run the commands manually:
```cmd
cd backend
python main.py
```

## Linux/Mac Users

For Linux/Mac users, make the script executable and run:
```bash
chmod +x start_services.sh
./start_services.sh
```

## Environment Configuration

Make sure your `.env` file has the correct configuration:
```
COHERE_API_KEY=your_cohere_api_key_here
SECRET_KEY=your_secret_key_here
```

The AI chatbot is now fully functional and ready for professional use!