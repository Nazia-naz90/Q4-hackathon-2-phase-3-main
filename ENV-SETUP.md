# Environment Configuration Setup

## Overview
This project uses a **centralized `.env` file** located at the project root for all environment variables. This ensures consistent configuration across all services (Backend, AI Agent, AI Integration).

## File Structure
```
q4-hackathone2-phase-3/
├── .env                          # Central configuration (DO NOT COMMIT!)
├── backend/
│   ├── .env                      # References root .env (safe to commit)
│   ├── main.py                   # Loads from root .env
│   └── database.py               # Loads from root .env
├── ai-agent/
│   ├── agent.py                  # Loads from root .env
│   └── main.py                   # Loads from root .env
└── ai-integration/
    └── main.py                   # Loads from root .env
```

## Environment Variables

### Required Variables (in root `.env`)

#### Database Configuration
```env
DATABASE_URL=postgresql+asyncpg://user:password@host/neondb?ssl=require
DATABASE_URL_UNPOOLED=postgresql://user:password@host/neondb?sslmode=require
POSTGRES_USER=neondb_owner
```

#### Authentication
```env
SECRET_KEY=your-secure-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

#### OpenAI API
```env
OPENAI_API_KEY=sk-proj-your-api-key-here
```

#### Service URLs
```env
BACKEND_URL=http://localhost:8000
AI_AGENT_URL=http://localhost:8001
```

#### Debug
```env
DEBUG=True
```

## How It Works

All Python modules load environment variables from the **root `.env`** file using:

```python
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)
```

## Security Notes

⚠️ **IMPORTANT:**
- Never commit the root `.env` file to version control
- The `.env` file contains sensitive credentials (API keys, database passwords)
- The `backend/.env` file is safe to commit as it only contains comments

## Starting the Services

### Option 1: Start all servers
```bash
# Windows
start-servers.bat

# Or manually:
# Backend (port 8000)
cd backend && uv run python main.py

# AI Integration (port 8001)
cd ai-integration && uv run python main.py
```

### Option 2: Development mode
```bash
# Backend with auto-reload
cd backend && uv run uvicorn main:app --reload --port 8000

# AI Integration with auto-reload
cd ai-integration && uv run uvicorn main:app --reload --port 8001
```

## Testing the Setup

1. **Check Backend Health:**
   ```
   GET http://localhost:8000/
   GET http://localhost:8000/ai/health
   ```

2. **Check AI Integration Health:**
   ```
   GET http://localhost:8001/health
   ```

3. **Test AI Chat:**
   ```bash
   POST http://localhost:8000/ai/chat
   Content-Type: application/json
   Authorization: Bearer YOUR_TOKEN
   
   {
     "message": "Create a task to buy groceries"
   }
   ```

## Troubleshooting

### "DATABASE_URL environment variable is required"
- Ensure root `.env` file exists and contains `DATABASE_URL`
- Check that the file is being loaded from the correct path

### "OPENAI_API_KEY not set"
- Verify `OPENAI_API_KEY` is set in root `.env`
- Restart the server after changing `.env`

### "SECRET_KEY must be set to a secure value"
- Update `SECRET_KEY` in root `.env` with a strong random value
- Never use the default value in production

## Migration from Old Setup

If you were previously using `backend/.env` for credentials:

1. ✅ Done: Root `.env` updated with all credentials
2. ✅ Done: `backend/.env` converted to reference file
3. ✅ Done: All modules updated to load from root `.env`
