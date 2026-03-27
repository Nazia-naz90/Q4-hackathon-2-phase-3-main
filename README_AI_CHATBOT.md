# AI Todo Assistant Chatbot Documentation

This document explains how to use the AI Todo Assistant Chatbot that's part of your Q4 Hackathon project.

## System Overview

Your project includes two components:
1. **Backend API** (port 8000) - Contains the AI chatbot functionality
2. **MCP Server & AI Agent** (separate components) - Alternative implementation

We'll focus on the backend AI chatbot since it's already implemented and functional.

## Prerequisites

1. Python 3.8+
2. Virtual environment activated
3. All dependencies installed via `pip install -r requirements.txt`

## Running the Backend API

You can start the backend server using uvicorn directly:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

This will start the API on `http://localhost:8000`

Alternatively, you can run the main.py file directly:
```bash
cd backend
python main.py
```

## How to Use the AI Chatbot

### 1. Create a User Account
First, create a user account:
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "yourusername",
    "email": "youremail@example.com",
    "password": "yourpassword"
  }'
```

### 2. Login to Get JWT Token
Login with your credentials to get an authentication token:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -d "username=yourusername&password=yourpassword"
```

### 3. Chat with the AI Assistant
Use the JWT token to chat with the AI:
```bash
curl -X POST "http://localhost:8000/ai/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a task to buy groceries"}'
```

## Supported Commands

The AI assistant understands natural language commands:

- **Create tasks**: "Create a task to buy groceries", "Add a task to finish the project"
- **List tasks**: "Show my tasks", "List all tasks", "What are my tasks?"
- **Complete tasks**: "Complete task [ID]", "Mark task as done"
- **Delete tasks**: "Delete task [ID]", "Remove task [ID]"
- **Help**: "What can you do?", "Help", "Commands"

## Quick Demo Script

We've provided a demo script to show how everything works:

```bash
python demo_ai_chatbot.py
```

This will:
1. Create a test user
2. Log in to get a token
3. Send several sample messages to the AI chatbot
4. Display the responses

## Troubleshooting

### Common Issues:

1. **Connection refused**: Make sure the backend server is running on port 8000
2. **Authentication failed**: Verify your username/password and token
3. **API key issues**: Check that COHERE_API_KEY is set in your .env file
4. **Database errors**: Ensure the database is properly configured

### Debugging Steps:

1. Check if backend is running:
   ```bash
   curl http://localhost:8000/
   ```

2. Check AI health:
   ```bash
   curl http://localhost:8000/ai/health
   ```

3. Test authentication:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
     -d "username=test&password=test"
   ```

## API Endpoints

- `POST /auth/signup` - Create new user
- `POST /auth/login` - Login and get JWT token
- `POST /ai/chat` - Chat with AI assistant (requires auth)
- `GET /ai/health` - Check AI service status
- `GET /health` - Check general API health

## Environment Variables

Make sure your `.env` file contains:
```
COHERE_API_KEY=your_actual_cohere_api_key_here
SECRET_KEY=your_secret_key_here
```

## Contributing

To extend the AI chatbot functionality:
1. Modify `backend/main.py` in the `process_ai_message_with_cohere` function
2. Add new command parsing logic
3. Extend the prompt engineering for better responses