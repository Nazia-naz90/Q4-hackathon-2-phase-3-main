# Todo Application - Phase 2

This is the Phase 2 implementation of the Todo Application with enhanced features including priority levels, due dates, and tags. The application includes both a CLI version and a full-stack web application with authentication.

## New Features

### Priority Levels
- Tasks can now have priority levels: Low, Medium, High
- Visual indicators for priority levels (color-coded badges)
- Filtering by priority level

### Due Dates
- Tasks can have due dates with time
- Visual indicators for overdue tasks (red color)
- Due date display in the task list

### Tags
- Create custom tags with color coding
- Tag management interface
- Tags display on tasks

### Enhanced UI/UX
- Search functionality to find tasks by title or description
- Multiple filtering options (status, priority)
- Improved task display with priority badges and due date indicators

## Tech Stack

- **Frontend**: Next.js 16+, TypeScript, Tailwind CSS
- **Backend**: Python 3.13+, FastAPI
- **Database**: PostgreSQL (Neon Serverless) with SQLModel
- **Authentication**: Better Auth with JWT
- **Package Management**: uv for Python, npm for frontend

## Project Structure

- `frontend/` - Next.js frontend application
- `backend/` - FastAPI backend application
- `src/` - CLI application (Phase 1)
- `specs/` - Feature specifications
- `history/` - Prompt History Records and ADRs
- `.specify/` - SpecKit Plus configuration

## API Endpoints

### Tasks
- `GET /api/tasks` - Get all tasks for authenticated user
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task
- `PATCH /api/tasks/{id}/complete` - Toggle task completion

### Tags
- `GET /api/tags` - Get all tags for authenticated user
- `POST /api/tags` - Create a new tag
- `PUT /api/tags/{id}` - Update a tag
- `DELETE /api/tags/{id}` - Delete a tag

## Environment Variables

### Backend (.env)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret for JWT token signing

### Frontend (.env.local)
- `NEXT_PUBLIC_API_BASE_URL` - Backend API URL
- `NEXT_PUBLIC_JWT_SECRET` - JWT secret (must match backend)

## Running the Application

### Backend
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
alembic upgrade head  # Run database migrations
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### CLI Application (Phase 1)
```bash
cd .
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
python main.py
```

## Database Migrations

To run migrations:
```bash
cd backend
alembic upgrade head
```

To create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

## Development Notes

This project represents Phase 2 of the Todo Application development, evolving from a simple CLI application to a full-stack web application with authentication and advanced features. The CLI version is maintained for backward compatibility and development purposes.