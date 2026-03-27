#!/bin/bash
# Start all services for the AI Todo Assistant

echo "Starting AI Todo Assistant services..."

# Start backend API using uvicorn
echo "Starting backend API with uvicorn..."
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Give backend time to start
sleep 3

# Test if backend is running
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend API is running on port 8000"
else
    echo "❌ Failed to start backend API"
    exit 1
fi

echo ""
echo "Services started successfully!"
echo "Backend API: http://localhost:8000"
echo "AI Chatbot: http://localhost:8000/ai/chat"
echo ""
echo "To test the AI chatbot:"
echo "1. Create a user: POST /auth/signup"
echo "2. Login: POST /auth/login"
echo "3. Chat: POST /ai/chat with Authorization header"
echo ""
echo "To stop services, run: kill $BACKEND_PID"