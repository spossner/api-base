# FastAPI Production-Ready API

A production-ready FastAPI application with best practices, structured architecture, and deployment configurations.

## Features

- ✅ **FastAPI Framework** - Modern, fast, high-performance web framework
- ✅ **Pydantic V2** - Data validation using Python type annotations
- ✅ **Structured Architecture** - Clean separation of concerns
- ✅ **API Versioning** - Support for multiple API versions
- ✅ **CORS Configuration** - Secure cross-origin resource sharing
- ✅ **Environment-based Settings** - Configuration management with pydantic-settings
- ✅ **Logging** - Comprehensive logging setup
- ✅ **Middleware** - Request logging and processing time tracking
- ✅ **Health Checks** - Built-in health check endpoint
- ✅ **Docker Support** - Multi-stage Dockerfile and docker-compose
- ✅ **Example CRUD Endpoints** - Items and Users resources
- ✅ **Input Validation** - Automatic request/response validation
- ✅ **Interactive API Docs** - Auto-generated Swagger UI and ReDoc

## Project Structure

```
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration settings
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py    # API router aggregator
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── items.py # Items CRUD endpoints
│   │           └── users.py # Users CRUD endpoints
│   └── core/
│       ├── __init__.py
│       ├── logging.py       # Logging configuration
│       └── middleware.py    # Custom middleware
├── logs/                    # Application logs (created at runtime)
├── venv/                    # Virtual environment
├── .env                     # Environment variables (not in repo)
├── .env.example             # Example environment variables
├── .gitignore              # Git ignore rules
├── .dockerignore           # Docker ignore rules
├── Dockerfile              # Production Docker image
├── docker-compose.yml      # Docker compose configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Prerequisites

- Python 3.8+
- pip
- (Optional) Docker and Docker Compose

## Installation

### 1. Clone the repository

```bash
cd C:\Users\micro\workspace\playground\fastapi
```

### 2. Create and activate virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows (Git Bash/MINGW)
source venv/Scripts/activate

# Activate on Windows (CMD)
venv\Scripts\activate.bat

# Activate on Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your settings
```

## Running the Application

### Quick Start with Makefile (Recommended)

The easiest way to run the application is using the included Makefile:

```bash
# Make sure virtual environment is activated
source venv/Scripts/activate  # or appropriate command for your shell

# View all available commands
make help

# Run in development mode with hot reload
make dev

# Run in DEBUG mode with verbose logging and detailed traces
make debug

# Run in production mode
make prod

# Install dependencies
make install

# Clean up cache files
make clean
```

### Manual Commands

#### Development Mode

```bash
# Make sure virtual environment is activated
source venv/Scripts/activate  # or appropriate command for your shell

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Debug Mode

```bash
# Run with debug logging and verbose output
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --access-log
```

#### Production Mode

```bash
# Run with multiple workers (recommended for production)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs (in debug mode)
- **ReDoc**: http://localhost:8000/redoc (in debug mode)
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

### Items API (`/api/v1/items`)

- `GET /api/v1/items` - List all items (with pagination)
- `GET /api/v1/items/{item_id}` - Get specific item
- `POST /api/v1/items` - Create new item
- `PUT /api/v1/items/{item_id}` - Update item
- `DELETE /api/v1/items/{item_id}` - Delete item

### Users API (`/api/v1/users`)

- `GET /api/v1/users` - List all users (with pagination)
- `GET /api/v1/users/{user_id}` - Get specific user
- `POST /api/v1/users` - Create new user
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

## Example Requests

### Create an Item

```bash
curl -X POST "http://localhost:8000/api/v1/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Widget",
    "description": "A useful widget",
    "price": 19.99,
    "tax": 1.99
  }'
```

### Create a User

```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "password": "secretpassword123"
  }'
```

## Configuration

Edit `.env` file to configure:

- Application name and version
- Debug mode
- API prefix
- CORS settings
- Server settings (host, port, workers)
- Logging level

## Development

### Adding New Endpoints

1. Create a new file in `app/api/v1/endpoints/`
2. Define your router and endpoints
3. Import and include the router in `app/api/v1/router.py`

### Adding Middleware

1. Create middleware in `app/core/middleware.py`
2. Add to the application in `app/main.py`

## Production Considerations

- ✅ Set `DEBUG=false` in production
- ✅ Use environment variables for sensitive data
- ✅ Configure proper CORS origins
- ✅ Use a reverse proxy (nginx) in front of the application
- ✅ Enable HTTPS/TLS
- ✅ Set up proper logging and monitoring
- ✅ Use a production ASGI server (uvicorn with multiple workers)
- ✅ Implement rate limiting
- ✅ Add authentication/authorization
- ✅ Use a real database instead of in-memory storage
- ✅ Implement proper error handling and validation

## Next Steps

1. **Add Database**: Integrate SQLAlchemy or another ORM
2. **Authentication**: Implement JWT-based authentication
3. **Rate Limiting**: Add rate limiting middleware
4. **Caching**: Implement Redis caching
5. **Testing**: Add pytest tests
6. **CI/CD**: Set up GitHub Actions or similar
7. **Monitoring**: Add Prometheus/Grafana or similar
8. **API Gateway**: Consider Kong or similar for production

## License

MIT

## Support

For issues and questions, please open an issue in the repository.
