# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
Also see @docs/prj-overview.md for an overview of the project.

## Project Architecture

This is a TODO application built with:
- **Backend**: FastAPI with JWT authentication
- **Frontend**: Vanilla HTML/JavaScript/CSS
- **Database**: MySQL 8.0
- **Deployment**: Docker Compose

### Backend Structure (FastAPI)
- **Entry point**: `api/main.py` - FastAPI app with CORS middleware and router registration
- **Database**: `api/db.py` - SQLAlchemy connection to MySQL with dependency injection
- **Routers**: `api/routers/` - API endpoints for tasks, users, and done status
- **CRUD operations**: `api/cruds/` - Raw SQL operations using SQLAlchemy text() 
- **Authentication**: `api/extra_modules/auth/` - JWT-based authentication system
- **Image handling**: `api/extra_modules/image/` - File upload processing including HEIF conversion

### Frontend Structure
- **Static files**: `frontend/` directory with HTML pages, CSS, and JavaScript
- **API client**: `frontend/js/api.js` - Fetch-based API calls to backend
- **Pages**: `index.html`, `login.html`, `signup.html`, `task-create.html`, etc.

### Key Architecture Notes
- Uses raw SQL queries instead of ORM models (via SQLAlchemy `text()`)
- JWT tokens stored in localStorage for authentication
- Image uploads converted from HEIF to JPEG automatically
- User isolation - users can only access their own tasks
- Database transactions handled manually with explicit commits

## Development Commands

### Project Startup
```bash
# Start the entire application
docker-compose up

# Access points:
# - API documentation: http://localhost:8000/docs
# - Frontend: http://localhost:3000
# - Database: localhost:33306 (MySQL)
```

### Package Management
```bash
# Add new Python packages (macOS)
sh script/add-package.sh <package-name>

# Add new Python packages (Windows)
script\add-package.bat <package-name>
```

### Testing
```bash
# Run end-to-end tests
python -m pytest tests/test_e2e.py

# Run with unittest
python -m unittest tests.test_e2e
```

### Code Quality
The project uses:
- Black formatter with line length 79 (configured in `pyproject.toml`)
- Poetry for dependency management
- Faker for test data generation

### Database Operations
- **Connection**: MySQL via PyMySQL driver at `root@db:3306/demo`
- **Schema**: Defined in `init.sql` (tables: users, tasks, dones)
- **Migrations**: Manual SQL changes through VS Code MySQL extension
- **Backups**: Stored in `api/db_back_up/` directory

## Important Implementation Details

### Authentication Flow
1. User registration/login via `/user` and `/token` endpoints
2. JWT tokens with HS256 algorithm (SECRET_KEY hardcoded - needs environment variable)
3. `get_current_user` dependency for protected routes
4. Tokens expire after 15 minutes by default

### Task Management
- Tasks have title, due_date, user_id, img_path fields
- Done status tracked in separate `dones` table
- Image uploads saved to `static/images/` with unique timestamps
- Full CRUD operations with user isolation

### Error Handling
- Consistent HTTP status codes (401, 403, 404, 422)
- Japanese error messages in frontend
- Comprehensive test coverage for edge cases

### File Structure Notes
- `book_fastapi_sample/` contains tutorial examples (can be ignored for development)
- `static/images/` stores uploaded task images
- `docs/` contains setup instructions for different OS platforms

## Testing Strategy
- End-to-end tests using TestClient and SQLite for isolation
- Faker for generating realistic test data
- User authentication flow testing
- Image upload testing (including HEIF format)
- Cross-user access permission testing

## Security Considerations
- JWT secret key currently hardcoded (should use environment variables)
- CORS configured for localhost:3000 only
- User isolation enforced at API level
- File upload validation for images